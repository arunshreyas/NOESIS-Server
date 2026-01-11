const { default: mongoose } = require("mongoose");

const userSchema = new mongoose.Schema(
  {
    user_id: {
      type: String,
      required: true,
      unique: true,
      default: () =>
        `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    },
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
    },

    username: {
      type: String,
      required: true,
      unique: true,
      trim: true,
    },

    passwordHash: {
      type: String,
      required: true,
    },

    filledForm: {
      type: Boolean,
      default: false,
    },

    role: {
      type: String,
      enum: ["student", "professional", "other"],
      default: "student",
    },
  },
  {
    timestamps: true,
  }
);
const User = mongoose.model("User", userSchema);
module.exports = User;
