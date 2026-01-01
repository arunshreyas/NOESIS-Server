from sqlalchemy import text
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.db.database import engine

def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(" Database connected:", result.scalar())

if __name__ == "__main__":
    test_connection()
