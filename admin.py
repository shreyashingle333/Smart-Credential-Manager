import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import csv
import datetime

DB_NAME = "credentials.db"

def view_users(root):

    win = tk.Toplevel(root)
    win.title("Users")

    tree = ttk.Treeview(
        win,
        columns=("id", "username", "role"),
        show="headings"
    )

    tree.heading("id", text="ID")
    tree.heading("username", text="Username")
    tree.heading("role", text="Role")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT id, username, role
        FROM users
    """)

    for row in c.fetchall():
        tree.insert("", "end", values=row)

    conn.close()

    tree.pack(expand=True, fill="both")

def view_logs(root):

    win = tk.Toplevel(root)
    win.title("Logs")

    tree = ttk.Treeview(
        win,
        columns=("id", "user_id", "action", "timestamp"),
        show="headings"
    )

    for col in ("id", "user_id", "action", "timestamp"):
        tree.heading(col, text=col.capitalize())

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM logs")

    for row in c.fetchall():
        tree.insert("", "end", values=row)

    conn.close()

    tree.pack(expand=True, fill="both")

def export_users():

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        SELECT username, role
        FROM users
    """)

    rows = c.fetchall()

    conn.close()

    filename = (
        f"users_export_"
        f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    )

    with open(filename, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow(["Username", "Role"])

        writer.writerows(rows)

    messagebox.showinfo(
        "Export",
        f"Users exported to {filename}"
    )