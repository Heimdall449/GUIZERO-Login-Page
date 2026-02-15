from tkinter import *
import csv
import os
import subprocess
import sys


"configuration"

_script_dir = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(_script_dir, "users.csv")
SIGNUP_PAGE = os.path.join(_script_dir, "signup.py")

# tkinter variable placeholders (will be initialized after `Tk()` exists)
username_entry = None
password_entry = None
error_text = None
error_label = None
error_fg = "red"


"utility functions"

#-------------check if username and password exist in csv--------------
def credentials_valid(username, password):
    """Return True if a row in the CSV has this username and password."""
    if not os.path.exists(CSV_FILE):
        return False
    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("username") == username and row.get("password") == password:
                return True
    return False


def open_success_window(username):
    success_window = Toplevel(app)
    success_window.title("Login Successful")
    success_window.geometry("320x120")
    Label(success_window, text=f"Welcome, {username}!", font=("Arial", 14)).pack(expand=True)
    Button(success_window, text="OK", command=success_window.destroy).pack(pady=10)


def open_signup():
    """Launch the signup page in a new Python process."""
    subprocess.Popen([sys.executable, SIGNUP_PAGE])


#-----------------GUI login handler---------------------
def login():
    error_text.set("")
    if error_label:
        error_label.config(fg=error_fg)

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        error_text.set("Please enter both username and password")
        if error_label:
            error_label.config(fg="red")
        return

    if credentials_valid(username, password):
        error_text.set("")
        if error_label:
            error_label.config(fg="green")
        open_success_window(username)
    else:
        error_text.set("Invalid username or password")
        if error_label:
            error_label.config(fg="red")


#-----------------main program app interface---------------------
app = Tk()
app.title("Login Page")
app.geometry("400x220")

username_entry = StringVar()
password_entry = StringVar()
error_fg = "red"

Label(app, text="Username:").pack()
Entry(app, textvariable=username_entry).pack()

Label(app, text="Password:").pack()
Entry(app, textvariable=password_entry, show="*").pack()

Button(app, text="Log In", command=login).pack(pady=8)
Button(app, text="Sign Up", command=open_signup).pack()

error_text = StringVar()
error_label = Label(app, textvariable=error_text, fg=error_fg)
error_label.pack(pady=8)

app.mainloop()
