
import customtkinter as ctk

from tkinter import (
    messagebox,
    simpledialog
)

import sqlite3
import time

from security import (
    hash_password,
    verify_password,
    check_strength
)

from database import (
    connect_db,
    log_action
)

from utils import (
    generate_random_password
)

from admin import (
    view_users,
    view_logs,
    export_users
)

# ================= SETTINGS =================

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 60

# ================= MAIN GUI CLASS =================

class CredentialManager:

    def __init__(self, root):

        self.root = root

        self.root.title("Smart Credential Manager")

        self.root.geometry("1000x700")

        self.username = None
        self.role = None

        self.failed_attempts = {}
        self.locked_users = {}

        self.show_login()

    # ================= CLEAR WINDOW =================

    def clear(self):

        for widget in self.root.winfo_children():

            widget.destroy()

    # ================= LOGIN PAGE =================

    def show_login(self):

        self.clear()

        frame = ctk.CTkFrame(self.root)

        frame.pack(
            pady=50,
            padx=50,
            fill="both",
            expand=True
        )

        title = ctk.CTkLabel(
            frame,
            text="Smart Credential Manager",
            font=("Arial", 32, "bold")
        )

        title.pack(pady=30)

        subtitle = ctk.CTkLabel(
            frame,
            text="Login to Continue",
            font=("Arial", 18)
        )

        subtitle.pack(pady=10)

        # Username

        self.user_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Username",
            width=350,
            height=45
        )

        self.user_entry.pack(pady=15)

        # Password

        self.pass_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Password",
            show="*",
            width=350,
            height=45
        )

        self.pass_entry.pack(pady=15)

        # Login Button

        login_btn = ctk.CTkButton(
            frame,
            text="Login",
            width=250,
            height=45,
            command=self.login
        )

        login_btn.pack(pady=20)

        # Register Button

        register_btn = ctk.CTkButton(
            frame,
            text="Register",
            width=250,
            height=45,
            command=self.show_register
        )

        register_btn.pack(pady=10)

        # Forgot Password Button

        forgot_btn = ctk.CTkButton(
            frame,
            text="Forgot Password",
            width=250,
            height=45,
            command=self.forgot_password
        )

        forgot_btn.pack(pady=10)

    # ================= LOGIN FUNCTION =================

    def login(self):

        username = self.user_entry.get()

        password = self.pass_entry.get()

        # Check lockout

        if username in self.locked_users:

            unlock_time = self.locked_users[username]

            if time.time() < unlock_time:

                remaining = int(
                    unlock_time - time.time()
                )

                messagebox.showerror(
                    "Locked",
                    f"Try again in {remaining} seconds"
                )

                return

        conn = connect_db()

        c = conn.cursor()

        c.execute("""
            SELECT id, password_hash, salt, role
            FROM users
            WHERE username=?
        """, (username,))

        user = c.fetchone()

        if user and verify_password(
            user[1],
            user[2],
            password
        ):

            self.username = username
            self.role = user[3]

            self.failed_attempts[username] = 0

            log_action(user[0], "login success")

            messagebox.showinfo(
                "Success",
                f"Welcome {username}"
            )

            self.show_dashboard()

        else:

            self.failed_attempts[username] = (
                self.failed_attempts.get(username, 0) + 1
            )

            if self.failed_attempts[username] >= MAX_LOGIN_ATTEMPTS:

                self.locked_users[username] = (
                    time.time() + LOCKOUT_TIME
                )

                messagebox.showerror(
                    "Locked",
                    "Too many failed attempts.\nAccount locked for 60 seconds."
                )

            else:

                remaining = (
                    MAX_LOGIN_ATTEMPTS -
                    self.failed_attempts[username]
                )

                messagebox.showerror(
                    "Error",
                    f"Invalid credentials\nAttempts left: {remaining}"
                )

        conn.close()

    # ================= REGISTER PAGE =================

    def show_register(self):

        self.clear()

        frame = ctk.CTkFrame(self.root)

        frame.pack(
            pady=50,
            padx=50,
            fill="both",
            expand=True
        )

        title = ctk.CTkLabel(
            frame,
            text="Create Account",
            font=("Arial", 30, "bold")
        )

        title.pack(pady=20)

        # Username

        self.reg_user = ctk.CTkEntry(
            frame,
            placeholder_text="Username",
            width=350,
            height=45
        )

        self.reg_user.pack(pady=10)

        # Password

        self.reg_pass = ctk.CTkEntry(
            frame,
            placeholder_text="Password",
            show="*",
            width=350,
            height=45
        )

        self.reg_pass.pack(pady=10)

        # Security Answer

        self.security_answer = ctk.CTkEntry(
            frame,
            placeholder_text="Favorite Color?",
            width=350,
            height=45
        )

        self.security_answer.pack(pady=10)

        # Register Button

        register_btn = ctk.CTkButton(
            frame,
            text="Register",
            width=250,
            height=45,
            command=self.register
        )

        register_btn.pack(pady=20)

        # Back Button

        back_btn = ctk.CTkButton(
            frame,
            text="Back to Login",
            width=250,
            height=45,
            command=self.show_login
        )

        back_btn.pack(pady=10)

    # ================= REGISTER FUNCTION =================

    def register(self):

        username = self.reg_user.get()

        password = self.reg_pass.get()

        security_answer = (
            self.security_answer.get().lower()
        )

        strength = check_strength(password)

        if strength == "Weak":

            messagebox.showerror(
                "Weak Password",
                "Password too weak"
            )

            return

        ph, salt = hash_password(password)

        try:

            conn = connect_db()

            c = conn.cursor()

            c.execute("""
                INSERT INTO users
                (username, password_hash, salt, role, security_answer)

                VALUES (?, ?, ?, ?, ?)
            """, (
                username,
                ph,
                salt,
                "user",
                security_answer
            ))

            conn.commit()

            conn.close()

            messagebox.showinfo(
                "Success",
                "User Registered Successfully"
            )

            self.show_login()

        except sqlite3.IntegrityError:

            messagebox.showerror(
                "Error",
                "Username already exists"
            )

    # ================= DASHBOARD =================

    def show_dashboard(self):

        self.clear()

        frame = ctk.CTkFrame(self.root)

        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        title = ctk.CTkLabel(
            frame,
            text=f"Welcome {self.username}",
            font=("Arial", 30, "bold")
        )

        title.pack(pady=30)

        # Change Password

        change_btn = ctk.CTkButton(
            frame,
            text="Change Password",
            width=300,
            height=45,
            command=self.change_password
        )

        change_btn.pack(pady=10)

        # Generate Password

        generate_btn = ctk.CTkButton(
            frame,
            text="Generate Password",
            width=300,
            height=45,
            command=self.generate_password
        )

        generate_btn.pack(pady=10)

        # Admin Features

        if self.role == "admin":

            users_btn = ctk.CTkButton(
                frame,
                text="View Users",
                width=300,
                height=45,
                command=lambda: view_users(self.root)
            )

            users_btn.pack(pady=10)

            logs_btn = ctk.CTkButton(
                frame,
                text="View Logs",
                width=300,
                height=45,
                command=lambda: view_logs(self.root)
            )

            logs_btn.pack(pady=10)

            export_btn = ctk.CTkButton(
                frame,
                text="Export Users",
                width=300,
                height=45,
                command=export_users
            )

            export_btn.pack(pady=10)

        # Logout

        logout_btn = ctk.CTkButton(
            frame,
            text="Logout",
            width=300,
            height=45,
            fg_color="red",
            hover_color="darkred",
            command=self.show_login
        )

        logout_btn.pack(pady=30)

    # ================= CHANGE PASSWORD =================

    def change_password(self):

        new_pass = simpledialog.askstring(
            "Password",
            "Enter new password",
            show="*"
        )

        if not new_pass:
            return

        messagebox.showinfo(
            "Success",
            "Password Changed Successfully"
        )

    # ================= GENERATE PASSWORD =================

    def generate_password(self):

        length = simpledialog.askinteger(
            "Password Length",
            "Enter length (8-20)"
        )

        if not length:
            return

        password = generate_random_password(length)

        messagebox.showinfo(
            "Generated Password",
            password
        )

       # ================= FORGOT PASSWORD =================

    def forgot_password(self):

        username = simpledialog.askstring(
            "Forgot Password",
            "Enter Username"
        )

        if not username:
            return

        answer = simpledialog.askstring(
            "Security Question",
            "What is your favorite color?"
        )

        if not answer:
            return

        conn = connect_db()

        c = conn.cursor()

        c.execute("""
            SELECT id, security_answer
            FROM users
            WHERE username=?
        """, (username,))

        user = c.fetchone()

        if not user:

            messagebox.showerror(
                "Error",
                "User not found"
            )

            conn.close()

            return

        stored_answer = user[1]

        if stored_answer.lower() != answer.lower():

            messagebox.showerror(
                "Error",
                "Wrong security answer"
            )

            conn.close()

            return

        new_password = simpledialog.askstring(
            "Reset Password",
            "Enter New Password",
            show="*"
        )

        if not new_password:

            conn.close()

            return

        strength = check_strength(new_password)

        if strength == "Weak":

            messagebox.showerror(
                "Weak Password",
                "Password too weak"
            )

            conn.close()

            return

        ph, salt = hash_password(new_password)

        c.execute("""
            UPDATE users

            SET password_hash=?,
                salt=?

            WHERE id=?
        """, (
            ph,
            salt,
            user[0]
        ))

        conn.commit()

        conn.close()

        messagebox.showinfo(
            "Success",
            "Password Reset Successful"
        )