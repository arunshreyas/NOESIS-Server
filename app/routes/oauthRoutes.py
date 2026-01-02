import base64
import hashlib
import os
import secrets
import time
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.oauthAccountModel import OAuthAccountModel
from app.models.userModel import UserModel
from app.utils.auth import create_access_token, get_password_hash

router = APIRouter(prefix="/auth", tags=["oauth"])


_STATE_TTL_SECONDS = 10 * 60
_state_store: dict[str, tuple[str, float]] = {}


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _pkce_pair() -> tuple[str, str]:
    verifier = _b64url(secrets.token_bytes(32))
    challenge = _b64url(hashlib.sha256(verifier.encode("ascii")).digest())
    return verifier, challenge


def _new_state() -> str:
    return _b64url(secrets.token_bytes(32))


def _save_state(state: str, code_verifier: str) -> None:
    _state_store[state] = (code_verifier, time.time() + _STATE_TTL_SECONDS)


def _pop_state(state: str) -> str | None:
    item = _state_store.pop(state, None)
    if not item:
        return None
    code_verifier, exp = item
    if time.time() > exp:
        return None
    return code_verifier


def _require_env(value: str | None, name: str) -> str:
    if not value:
        raise HTTPException(status_code=500, detail=f"Missing env var: {name}")
    return value


@router.get("/{provider}/login")
def oauth_login(provider: str):
    provider = provider.lower()

    if provider == "google":
        client_id = _require_env(getattr(settings, "GOOGLE_CLIENT_ID", None), "GOOGLE_CLIENT_ID")
        redirect_uri = _require_env(getattr(settings, "GOOGLE_REDIRECT_URI", None), "GOOGLE_REDIRECT_URI")
        scope = "openid email profile"
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    elif provider == "github":
        client_id = _require_env(getattr(settings, "GITHUB_CLIENT_ID", None), "GITHUB_CLIENT_ID")
        redirect_uri = _require_env(getattr(settings, "GITHUB_REDIRECT_URI", None), "GITHUB_REDIRECT_URI")
        scope = "read:user user:email"
        auth_url = "https://github.com/login/oauth/authorize"
    elif provider == "discord":
        client_id = _require_env(getattr(settings, "DISCORD_CLIENT_ID", None), "DISCORD_CLIENT_ID")
        redirect_uri = _require_env(getattr(settings, "DISCORD_REDIRECT_URI", None), "DISCORD_REDIRECT_URI")
        scope = "identify email"
        auth_url = "https://discord.com/api/oauth2/authorize"
    else:
        raise HTTPException(status_code=404, detail="Unknown provider")

    code_verifier, code_challenge = _pkce_pair()
    state = _new_state()
    _save_state(state, code_verifier)

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scope,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    return {"auth_url": f"{auth_url}?{urlencode(params)}"}


async def _exchange_code(provider: str, code: str, code_verifier: str) -> dict:
    if provider == "google":
        token_url = "https://oauth2.googleapis.com/token"
        client_id = _require_env(getattr(settings, "GOOGLE_CLIENT_ID", None), "GOOGLE_CLIENT_ID")
        client_secret = _require_env(getattr(settings, "GOOGLE_CLIENT_SECRET", None), "GOOGLE_CLIENT_SECRET")
        redirect_uri = _require_env(getattr(settings, "GOOGLE_REDIRECT_URI", None), "GOOGLE_REDIRECT_URI")
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
    elif provider == "github":
        token_url = "https://github.com/login/oauth/access_token"
        client_id = _require_env(getattr(settings, "GITHUB_CLIENT_ID", None), "GITHUB_CLIENT_ID")
        client_secret = _require_env(getattr(settings, "GITHUB_CLIENT_SECRET", None), "GITHUB_CLIENT_SECRET")
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "code_verifier": code_verifier,
        }
        headers = {"Accept": "application/json"}
    elif provider == "discord":
        token_url = "https://discord.com/api/oauth2/token"
        client_id = _require_env(getattr(settings, "DISCORD_CLIENT_ID", None), "DISCORD_CLIENT_ID")
        client_secret = _require_env(getattr(settings, "DISCORD_CLIENT_SECRET", None), "DISCORD_CLIENT_SECRET")
        redirect_uri = _require_env(getattr(settings, "DISCORD_REDIRECT_URI", None), "DISCORD_REDIRECT_URI")
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
    else:
        raise HTTPException(status_code=404, detail="Unknown provider")

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(token_url, data=data, headers=headers)
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {resp.text}")
        return resp.json()


async def _fetch_profile(provider: str, access_token: str) -> tuple[str, str, str]:
    async with httpx.AsyncClient(timeout=20) as client:
        if provider == "google":
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if resp.status_code >= 400:
                raise HTTPException(status_code=400, detail=f"Userinfo failed: {resp.text}")
            data = resp.json()
            provider_user_id = str(data.get("sub") or "")
            email = str(data.get("email") or "")
            username = str(data.get("name") or data.get("email") or "user")
            return provider_user_id, email, username

        if provider == "github":
            user_resp = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"},
            )
            if user_resp.status_code >= 400:
                raise HTTPException(status_code=400, detail=f"GitHub user failed: {user_resp.text}")
            user = user_resp.json()
            provider_user_id = str(user.get("id") or "")
            username = str(user.get("login") or "user")
            email = user.get("email")
            if not email:
                emails_resp = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"},
                )
                if emails_resp.status_code >= 400:
                    raise HTTPException(status_code=400, detail=f"GitHub emails failed: {emails_resp.text}")
                emails = emails_resp.json()
                primary = next((e for e in emails if e.get("primary")), None)
                verified = next((e for e in emails if e.get("verified")), None)
                choice = primary or verified or (emails[0] if emails else None)
                email = choice.get("email") if choice else ""
            return provider_user_id, str(email or ""), username

        if provider == "discord":
            resp = await client.get(
                "https://discord.com/api/users/@me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if resp.status_code >= 400:
                raise HTTPException(status_code=400, detail=f"Discord user failed: {resp.text}")
            data = resp.json()
            provider_user_id = str(data.get("id") or "")
            email = str(data.get("email") or "")
            username = str(data.get("username") or "user")
            return provider_user_id, email, username

    raise HTTPException(status_code=404, detail="Unknown provider")


@router.get("/{provider}/callback")
async def oauth_callback(provider: str, code: str, state: str, db: Session = Depends(get_db)):
    provider = provider.lower()
    code_verifier = _pop_state(state)
    if not code_verifier:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    tokens = await _exchange_code(provider, code, code_verifier)
    access_token = tokens.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Provider did not return access_token")

    provider_user_id, email, username = await _fetch_profile(provider, access_token)
    if not provider_user_id:
        raise HTTPException(status_code=400, detail="Missing provider user id")

    oauth = (
        db.query(OAuthAccountModel)
        .filter(
            (OAuthAccountModel.provider == provider)
            & (OAuthAccountModel.provider_user_id == provider_user_id)
        )
        .first()
    )

    user: UserModel | None = None
    if oauth:
        user = db.query(UserModel).filter(UserModel.id == oauth.user_id).first()

    if not user and email:
        user = db.query(UserModel).filter(UserModel.email == email).first()

    if not user:
        if not email:
            email = f"{provider_user_id}@{provider}.oauth"
        random_password = secrets.token_urlsafe(32)
        user = UserModel(
            username=username[:30],
            email=email,
            hashed_password=get_password_hash(random_password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not oauth:
        oauth = OAuthAccountModel(
            provider=provider,
            provider_user_id=provider_user_id,
            user_id=user.id,
        )
        db.add(oauth)
        db.commit()

    token = create_access_token({"sub": str(user.id)})

    redirect_url = _require_env(getattr(settings, "REDIRECT_URL", None), "REDIRECT_URL")
    sep = "&" if ("?" in redirect_url) else "?"
    return RedirectResponse(url=f"{redirect_url}{sep}token={token}")
