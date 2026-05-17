import random
import string
import os
import sqlite3
import hashlib
import binascii
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import csv
import datetime

# ==================== SECURITY HELPERS ====================

# Hash password with PBKDF2-HMAC
def hash_password(password: str) -> tuple[str, str]:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return binascii.hexlify(dk).decode(), binascii.hexlify(salt).decode()

# Verify password
def verify_password(stored_password: str, stored_salt: str, provided_password: str) -> bool:
    salt = binascii.unhexlify(stored_salt.encode())
    dk = hashlib.pbkdf2_hmac("sha256", provided_password.encode(), salt, 100000)
    return binascii.hexlify(dk).decode() == stored_password

# Password strength checker
def check_strength(password: str) -> str:
    strength = 0
    if any(c.islower() for c in password):
        strength += 1
    if any(c.isupper() for c in password):
        strength += 1
    if any(c.isdigit() for c in password):
        strength += 1
    if any(c in string.punctuation for c in password):
        strength += 1
    if len(password) >= 8:
        strength += 1

    if strength <= 2:
        return "Weak"
    elif strength == 3:
        return "Medium"
    else:
        return "Strong"

# ==================== DATABASE SETUP ====================

def init_db():
    conn = sqlite3.connect("credentials.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password_hash TEXT,
                    salt TEXT,
                    role TEXT DEFAULT 'user')''')
    c.execute('''CREATE TABLE IF NOT EXISTS password_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    password_hash TEXT,
                    salt TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Ensure default admin exists
def ensure_admin():
    conn = sqlite3.connect("credentials.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not c.fetchone():
        ph, salt = hash_password("Admin@123")
        c.execute("INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
                  ("admin", ph, salt, "admin"))
        conn.commit()
    conn.close()

# ==================== MAIN APPLICATION ====================

class CredentialManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Credential Manager")
        self.root.geometry("600x400")
        self.username = None
        self.role = None

        self.show_login()

    # ---------------- LOGIN SCREEN ----------------
    def show_login(self):
        self.clear()
        tk.Label(self.root, text="Login", font=("Arial", 18)).pack(pady=10)
        tk.Label(self.root, text="Username").pack()
        self.user_entry = tk.Entry(self.root)
        self.user_entry.pack(pady=5)
        tk.Label(self.root, text="Password").pack()
        self.pass_entry = tk.Entry(self.root, show="*")
        self.pass_entry.pack(pady=5)
        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Register", command=self.show_register).pack(pady=5)
        tk.Button(self.root, text="Forgot Password", command=self.forgot_password).pack(pady=5)

    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        conn = sqlite3.connect("credentials.db")
        c = conn.cursor()
        c.execute("SELECT id, password_hash, salt, role FROM users WHERE username=?", (username,))
        user = c.fetchone()
        if user and verify_password(user[1], user[2], password):
            self.username = username
            self.role = user[3]
            c.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user[0], "login success"))
            conn.commit()
            conn.close()
            self.show_dashboard()
        else:
            if user:
                c.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user[0], "login failed"))
                conn.commit()
            conn.close()
            messagebox.showerror("Error", "Invalid credentials")

    # ---------------- REGISTER SCREEN ----------------
    def show_register(self):
        self.clear()
        tk.Label(self.root, text="Register", font=("Arial", 18)).pack(pady=10)
        tk.Label(self.root, text="Username").pack()
        self.reg_user = tk.Entry(self.root)
        self.reg_user.pack(pady=5)
        tk.Label(self.root, text="Password").pack()
        self.reg_pass = tk.Entry(self.root, show="*")
        self.reg_pass.pack(pady=5)
        tk.Button(self.root, text="Register", command=self.register).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_login).pack()

    def register(self):
        username = self.reg_user.get()
        password = self.reg_pass.get()
        strength = check_strength(password)
        if strength == "Weak":
            messagebox.showerror("Error", "Password too weak")
            return
        ph, salt = hash_password(password)
        conn = sqlite3.connect("credentials.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
                      (username, ph, salt, "user"))
            conn.commit()
            messagebox.showinfo("Success", "User registered")
            self.show_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        conn.close()

    # ---------------- DASHBOARD ----------------
    def show_dashboard(self):
        self.clear()
        tk.Label(self.root, text=f"Welcome {self.username} ({self.role})", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Change Password", command=self.change_password).pack(pady=5)
        tk.Button(self.root, text="Generate Password", command=self.generate_password).pack(pady=5)
        if self.role == "admin":
            tk.Button(self.root, text="View Users", command=self.view_users).pack(pady=5)
            tk.Button(self.root, text="View Logs", command=self.view_logs).pack(pady=5)
            tk.Button(self.root, text="Export Users", command=self.export_users).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.show_login).pack(pady=10)

    # ---------------- CHANGE PASSWORD ----------------
    def change_password(self):
        new_pass = simpledialog.askstring("Change Password", "Enter new password", show="*")
        if not new_pass:
            return
        strength = check_strength(new_pass)
        if strength == "Weak":
            messagebox.showerror("Error", "Password too weak")
            return
        conn = sqlite3.connect("credentials.db")
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=?", (self.username,))
        user_id = c.fetchone()[0]
        # Check last 3 passwords
        c.execute("SELECT password_hash, salt FROM password_history WHERE user_id=? ORDER BY changed_at DESC LIMIT 3", (user_id,))
        history = c.fetchall()
        for h in history:
            if verify_password(h[0], h[1], new_pass):
                messagebox.showerror("Error", "Cannot reuse recent password")
                conn.close()
                return
        ph, salt = hash_password(new_pass)
        c.execute("UPDATE users SET password_hash=?, salt=? WHERE id=?", (ph, salt, user_id))
        c.execute("INSERT INTO password_history (user_id, password_hash, salt) VALUES (?, ?, ?)", (user_id, ph, salt))
        c.execute("INSERT INTO logs (user_id, action) VALUES (?, ?)", (user_id, "password changed"))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Password updated")

    # ---------------- GENERATE PASSWORD ----------------
    def generate_password(self):
        length = simpledialog.askinteger("Generate Password", "Enter length (8-20)")
        if not length or length < 8 or length > 20:
            messagebox.showerror("Error", "Invalid length")
            return
        all_chars = string.ascii_letters + string.digits + string.punctuation
        password = "".join(random.sample(all_chars, length))
        strength = check_strength(password)
        messagebox.showinfo("Generated", f"Password: {password}\nStrength: {strength}")

    # ---------------- ADMIN FEATURES ----------------
    def view_users(self):
        win = tk.Toplevel(self.root)
        win.title("Users")
        tree = ttk.Treeview(win, columns=("id", "username", "role"), show="headings")
        tree.heading("id", text="ID")
        tree.heading("username", text="Username")
        tree.heading("role", text="Role")
        conn = sqlite3.connect("credentials.db")
        c = conn.cursor()
        c.execute("SELECT id, username, role FROM users")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()
        tree.pack(expand=True, fill="both")

    def view_logs(self):
        win = tk.Toplevel(self.root)
        win.title("Logs")
        tree = ttk.Treeview(win, columns=("id", "user_id", "action", "timestamp"), show="headings")
        for col in ("id", "user_id", "action", "timestamp"):
            tree.heading(col, text=col.capitalize())
        conn = sqlite3.connect("credentials.db")
        c = conn.cursor()
        c.execute("SELECT * FROM logs")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()
        tree.pack(expand=True, fill="both")

    def export_users(self):
        conn = sqlite3.connect("credentials.db")
        c = conn.cursor()
        c.execute("SELECT username, password_hash, salt, role FROM users")
        rows = c.fetchall()
        conn.close()
        filename = f"users_export_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Username", "Password Hash", "Salt", "Role"])
            writer.writerows(rows)
        messagebox.showinfo("Export", f"Users exported to {filename}")

    # ---------------- FORGOT PASSWORD ----------------
    def forgot_password(self):
        username = simpledialog.askstring("Forgot Password", "Enter your username")
        if not username:
            return
        new_pass = simpledialog.askstring("Reset Password", "Enter new password", show="*")
        if not new_pass:
            return
        ph, salt = hash_password(new_pass)
        conn = sqlite3.connect("credentials.db")
        c = conn.cursor()
        c.execute("UPDATE users SET password_hash=?, salt=? WHERE username=?", (ph, salt, username))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Password reset")

    # ---------------- UTIL ----------------
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# ==================== MAIN ====================

if __name__ == "__main__":
    init_db()
    ensure_admin()
    root = tk.Tk()
    app = CredentialManager(root)
    root.mainloop()
