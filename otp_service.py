import random
import smtplib

def generate_otp():

    return str(
        random.randint(100000, 999999)
    )

def send_otp(receiver_email, otp):

    sender_email = "yourgmail@gmail.com"

    app_password = "your_app_password"

    message = f"Your OTP is {otp}"

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(
        sender_email,
        app_password
    )

    server.sendmail(
        sender_email,
        receiver_email,
        message
    )

    server.quit()