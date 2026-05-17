LIGHT = "light"

DARK = "dark"

def toggle_theme():

    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("light")
    else:
        ctk.set_appearance_mode("dark")