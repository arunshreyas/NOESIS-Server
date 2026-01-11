const mongoose = require("mongoose");

const connectDB = async () => {
  try {
    const mongoURI = process.env.DATABASE_URI;
    if (!mongoURI) {
      console.warn("No MongoDB URI provided. Skipping DB connection.");
      return;
    }
    await mongoose.connect(mongoURI);
    console.log("MongoDB connected");
  } catch (err) {
    console.error("MongoDB connection error:", err);
    console.warn(
      "Continuing without database connection. Set DATABASE_URL or start MongoDB to enable DB access."
    );
  }
};

module.exports = connectDB;
