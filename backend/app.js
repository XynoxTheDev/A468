const express = require("express");
const bcrypt = require("bcrypt");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const PORT = process.env.PORT || 5500;

// SQLite database setup
const db = new sqlite3.Database(":memory:"); // In-memory database for demonstration

// Create users table
db.serialize(() => {
  db.run(
    "CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT)"
  );
});

// Login route
app.post("/login", (req, res) => {
  // Implement login functionality here
});

// Signup route
app.post("/signup", (req, res) => {
  // Implement signup functionality here
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
