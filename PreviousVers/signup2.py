
# -------------------------------------------------------------
# GUIZERO-Login-Page/signup.py
# Signup system with sorted user data and validation
# -------------------------------------------------------------
# This file implements a signup GUI using tkinter. It validates usernames and passwords,
# ensures the user data CSV is always sorted alphabetically by username, and rewrites
# the file after each signup. Error handling and user feedback are provided in colour.
# -------------------------------------------------------------

" Imports "
from tkinter import *
import csv
import os
import subprocess
import sys

# allow importing User utilities located in parent workspace
_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(_script_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from User import (
    FIELDNAMES,
    is_email_valid,
    is_name_valid,
    is_age_valid,
    is_form_valid,
    is_subjects_valid,
    is_username_valid,
    is_password_valid,
)


"configuration"

# --- Configuration ---
_script_dir = os.path.dirname(os.path.abspath(__file__)) # Directory of the current script
CSV_FILE = os.path.join(_script_dir, "users.csv")  # Path to user data CSV
LOGIN_PAGE = os.path.join(_script_dir, "login.py")  # Path to login page


def create_csv_if_missing():
    """Create CSV with header if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def save_user(username, password, name='', age='', email='', form='', subjects='', csv_path=None):
    """Append new user then rewrite CSV sorted by username.

    Uses the header defined by `FIELDNAMES`.
    """
    if csv_path is None:
        csv_path = CSV_FILE

    records = []
    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)

    new = {
        'username': username,
        'password': password,
        'name': name,
        'age': age,
        'email': email,
        'form': form,
        'subjects': subjects,
    }
    records.append(new)
    records.sort(key=lambda r: (r.get('username') or '').lower())

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def open_login():
    """Launch the login page in a new Python process."""
    subprocess.Popen([sys.executable, LOGIN_PAGE])


def open_success_window():
    """Open a small window to indicate signup success."""
    success_window = Toplevel()
    success_window.title("Success")
    success_window.geometry("300x120")
    Label(success_window, text="Signup Successful!", font=("Arial", 14)).pack(expand=True)
    Button(success_window, text="OK", command=success_window.destroy).pack(pady=8)


def signup():
    """Handler for sign up button: validate fields and save user."""
    # clear previous message
    try:
        error_text.set("")
    except Exception:
        pass

    username = username_entry.get().strip()
    name_val = name_entry.get().strip()
    age_val = age_entry.get().strip()
    email = email_entry.get().strip()
    form_val = form_entry.get().strip()
    subjects_val = subjects_entry.get().strip()
    password = password_entry.get().strip()
    confirm = confirm_entry.get().strip()

    username_error = is_username_valid(username)
    if username_error:
        error_text.set(username_error)
        if error_label:
            error_label.config(fg="red")
        return

    if not is_name_valid(name_val):
        error_text.set("Name can only contain letters and spaces")
        if error_label:
            error_label.config(fg="red")
        return

    if not is_age_valid(age_val):
        error_text.set("Age must be a positive integer less than 150")
        if error_label:
            error_label.config(fg="red")
        return

    if not is_email_valid(email):
        error_text.set("Invalid email format")
        if error_label:
            error_label.config(fg="red")
        return

    if not is_form_valid(form_val):
        error_text.set("Form must be e.g. 12A or 9")
        if error_label:
            error_label.config(fg="red")
        return

    if not is_subjects_valid(subjects_val):
        error_text.set("Subjects must be comma-separated words")
        if error_label:
            error_label.config(fg="red")
        return

    if password != confirm:
        error_text.set("Passwords do not match")
        if error_label:
            error_label.config(fg="red")
        return

    pw_err = is_password_valid(username, password)
    if pw_err:
        error_text.set(pw_err)
        if error_label:
            error_label.config(fg="red")
        return

    save_user(username, password, name_val, age_val, email, form_val, subjects_val)
    error_text.set("Signup successful!")
    if error_label:
        error_label.config(fg="green")
    open_success_window()


# -------------------------------------------------------------
# Main program app interface (Tkinter GUI setup)
# -------------------------------------------------------------
def _build_gui():
    """Construct the signup window and start the Tk event loop."""

    create_csv_if_missing()  # Ensure the CSV file exists before starting the app

    global app, username_entry, name_entry, age_entry, email_entry
    global form_entry, subjects_entry, password_entry, confirm_entry
    global error_text, error_label, error_fg

    app = Tk()
    app.title("Signup Page")
    app.geometry("800x300")

    # Create tkinter variables AFTER the main Tk root exists
    username_entry = StringVar()
    name_entry = StringVar()
    age_entry = StringVar()
    email_entry = StringVar()
    form_entry = StringVar()
    subjects_entry = StringVar()
    password_entry = StringVar()
    confirm_entry = StringVar()
    error_fg = "red"

    # Build the UI using Label (not Text) for labels
    Label(app, text="Username:").pack()
    Entry(app, textvariable=username_entry).pack()

    Label(app, text="Name:").pack()
    Entry(app, textvariable=name_entry).pack()

    Label(app, text="Email:").pack()
    Entry(app, textvariable=email_entry).pack()

    Label(app, text="Age:").pack()
    Entry(app, textvariable=age_entry).pack()

    Label(app, text="Form:").pack()
    Entry(app, textvariable=form_entry).pack()

    Label(app, text="Subjects (comma-separated):").pack()
    Entry(app, textvariable=subjects_entry).pack()

    Label(app, text="Password:").pack()
    Entry(app, textvariable=password_entry, show="*").pack()

    Label(app, text="Confirm Password:").pack()
    Entry(app, textvariable=confirm_entry, show="*").pack()

    Button(app, text="Sign Up", command=signup).pack()
    Button(app, text="Log In", command=open_login).pack()

    # Label bound to `error_text`; we'll adjust its fg in `signup()` as needed
    error_text = StringVar()  # Initialize the error_text variable
    error_label = Label(app, textvariable=error_text, fg=error_fg)
    error_label.pack()

    # Start the GUI event loop
    app.mainloop()


if __name__ == "__main__":
    _build_gui()