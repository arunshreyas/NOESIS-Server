const User = require("../models/userModel");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const asyncHandler = require("express-async-handler");
const path = require("path");
const fs = require("fs");
require("dotenv").config({ path: path.resolve(__dirname, "../.env") });

const generateToken = (id) => {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error(
      "JWT_SECRET is not set. Please set JWT_SECRET in your .env file"
    );
  }
  const expiresIn = process.env.JWT_EXPIRES_IN || "30d";
  return jwt.sign({ id }, secret, { expiresIn });
};

//fetch users
const fetchUsers = asyncHandler(async (req, res) => {
  const users = await User.find({}).select("-passwordHash");
  if (!users?.length) {
    res.status(404).json({ message: "No users found" });
  }
  res.json(users);
});

//get current user
const getCurrentUser = asyncHandler(async (req, res) => {
  const user = await User.findById(req.user.id).select("-passwordHash");
  if (!user) {
    res.status(404);
    throw new Error("User not found");
  }
  res.json({
    user: {
      ...user.toObject(),
      profile_picture: user.profile_picture,
    },
  });
});

//get user by id
const getUserById = asyncHandler(async (req, res) => {
  const user = await User.findById(req.params.id).select("-passwordHash");
  if (!user) {
    res.status(404);
    throw new Error("User not found");
  }
  res.json({
    user: {
      ...user.toObject(),
      profile_picture: user.profile_picture,
    },
  });
});

//login
const loginUser = asyncHandler(async (req, res) => {
  const { email, password } = await User.findOne({ email: req.body.email });
  if (!email || !password) {
    res.status(400);
    throw new Error("Please provide email and password");
  }
  const user = await User.findOne({ email: req.body.email });
  if (user && (await bcrypt.compare(req.body.password, user.passwordHash))) {
    res.json({
      _id: user.id,
      email: user.email,
      username: user.username,
      role: user.role,
      token: generateToken(user._id),
    });
  } else {
    res.status(401);
    throw new Error("Invalid email or password");
  }
});

//signup
const signupUser = asyncHandler(async (req, res) => {
  const { email, username, password, role } = req.body;
  if (!email || !username || !password) {
    res.status(400);
    throw new Error("Please provide email, username and password");
  }
  const userExists = await User.findOne({ email });
  if (userExists) {
    res.status(400);
    throw new Error("User already exists");
  }
  const salt = await bcrypt.genSalt(10);
  const passwordHash = await bcrypt.hash(password, salt);
  const user = await User.create({
    email,
    username,
    passwordHash,
    role,
  });
  if (user) {
    res.status(201).json({
      _id: user.id,
      email: user.email,
      username: user.username,
      role: user.role,
      token: generateToken(user._id),
    });
  } else {
    res.status(400);
    throw new Error("Invalid user data");
  }
});

module.exports = {
  fetchUsers,
  getCurrentUser,
  getUserById,
  loginUser,
  signupUser,
};
