require("dotenv").config();
const express = require("express");
const app = express();
const path = require("path");
const PORT = process.env.PORT || 3000;
const connectDB = require("./config/dbConn");
const mongoose = require("mongoose");
const userRoutes = require("./routes/userRoutes");

connectDB();

app.use(express.json());

app.use("/", express.static(path.join(__dirname, "./public")));

app.use("/", require("./routes/root"));
app.use("/users", userRoutes);
app.use((req, res) => {
  res.status(404);
  if (req.accepts("html")) {
    res.sendFile(path.join(__dirname, "views", "404.html"));
  } else if (req.accepts("json")) {
    res.json({ error: "404 Not Found" });
  } else {
    res.type("txt").send("404 Not Found");
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  mongoose.connection.once("open", () => {
    console.log("Connected to MongoDB");
  });
  mongoose.connection.on("error", (err) => {
    console.log(err);
  });
});
