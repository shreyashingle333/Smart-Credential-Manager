from tkinter import filedialog

def upload_profile():

    file_path = filedialog.askopenfilename()

    return file_path

from PIL import Image, ImageTk

img = Image.open(file_path)

img = img.resize((100, 100))

photo = ImageTk.PhotoImage(img)