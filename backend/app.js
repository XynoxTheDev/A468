// app.js

const express = require("express");
const bcrypt = require("bcrypt");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const PORT = process.env.PORT || 2000;

// SQLite database setup
const db = new sqlite3.Database("users.db");

// Create users table if not exists
db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)`);

// Middleware for JSON parsing
app.use(express.json());

// Login route
app.post("/login", (req, res) => {
  const { email, password } = req.body;

  // Find user in the database
  db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: "Internal server error" });
    }
    if (!user) {
      return res.status(401).json({ error: "Invalid email or password" });
    }

    // Compare hashed password with input password
    bcrypt.compare(password, user.password, (err, result) => {
      if (err || !result) {
        return res.status(401).json({ error: "Invalid email or password" });
      }
      return res.status(200).json({ message: "Login successful" });
    });
  });
});

// Signup route
app.post("/signup", (req, res) => {
  const { email, password } = req.body;

  // Hash password using bcrypt
  bcrypt.hash(password, 10, (err, hash) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: "Internal server error" });
    }

    // Store user in the database
    db.run(
      "INSERT INTO users (email, password) VALUES (?, ?)",
      [email, hash],
      (err) => {
        if (err) {
          console.error(err);
          return res.status(400).json({ error: "User already exists" });
        }
        return res.status(201).json({ message: "Signup successful" });
      }
    );
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: "Internal server error" });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
