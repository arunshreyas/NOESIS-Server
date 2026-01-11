const express = require("express");
const mongoose = require("mongoose");
const router = express.Router();
const {
  fetchUsers,
  getCurrentUser,
  getUserById,
  loginUser,
  signupUser,
} = require("../controllers/userController");

const validateSignup = (req, res, next) => {
  const { email, username, password } = req.body;
  if (!email || !username || !password) {
    return res
      .status(400)
      .json({ message: "email, username and password are required" });
  }
  next();
};

const validateLogin = (req, res, next) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ message: "email and password are required" });
  }
  next();
};

router.param("id", (req, res, next, id) => {
  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ message: "Invalid user id" });
  }
  next();
});

router.post("/signup", validateSignup, signupUser);
router.post("/", validateSignup, signupUser); // alias for backwards-compat
router.post("/login", validateLogin, loginUser);
router.get("/", fetchUsers);
router.get("/me", getCurrentUser);
router.get("/:id", getUserById);

module.exports = router;
