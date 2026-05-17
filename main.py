import customtkinter as ctk

from database import (
    init_db,
    ensure_admin
)

from gui import CredentialManager

ctk.set_appearance_mode("dark")

ctk.set_default_color_theme("blue")

init_db()

ensure_admin()

root = ctk.CTk()

root.title("Smart Credential Manager")

root.geometry("1000x700")

app = CredentialManager(root)

root.mainloop()