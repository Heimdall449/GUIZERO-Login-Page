
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
import re
import subprocess
import sys


"configuration"

# --- Configuration ---
_script_dir = os.path.dirname(os.path.abspath(__file__)) # Directory of the current script
CSV_FILE = os.path.join(_script_dir, "users.csv")  # Path to user data CSV
LOGIN_PAGE = os.path.join(_script_dir, "login.py")  # Path to login page

# tkinter variable placeholders (will be initialized after `Tk()` exists) - at the end of the file, after the main Tk root is created, we will set these to StringVar() instances that can be used in the GUI

# Tkinter variable placeholders (initialized after Tk() exists) - in other words, these are just None for now and will be set to StringVar() after the main Tk root is created
username_entry = None
password_entry = None
confirm_entry = None
error_text = None
error_label = None
error_fg = "red"


"utility functions" # these are the functions that handle the core logic of the signup process, such as loading user data, validating input, and managing the CSV file. They are defined before the main GUI code to keep the structure organized and maintainable.

# -------------------------------------------------------------
# File creation utility
# -------------------------------------------------------------
def create_csv_if_missing():
    """
    Create the CSV file with headers if it doesn't exist.
    Ensures file handling logic is robust.
    """
    if not os.path.exists(CSV_FILE): # Check if the CSV file exists
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password"]) # Write the header row to the CSV file


# -------------------------------------------------------------
# Username validation utilities
# -------------------------------------------------------------
def username_exists(username):
    """
    Check if the username already exists in the CSV file.
    Returns True if found, False otherwise.
    Handles missing file gracefully.
    """
    if not os.path.exists(CSV_FILE):
        return False
    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)
        return any(row.get("username") == username for row in reader)

def is_username_valid(username):
    """
    Validate the username based on length, allowed characters, and uniqueness.
    Returns an error message string if invalid, or None if valid.
    """
    if not 5 <= len(username) <= 20:
        return "Username must be 5–20 characters long"
    if not re.match(r"^\w+$", username):
        return "Username can only contain letters, numbers, and underscores"
    if username_exists(username):
        return "Username already exists"
    return None


# -------------------------------------------------------------
# Password validation utilities
# -------------------------------------------------------------
def is_password_similar(username, password):
    """
    Check if the password is too similar to the username (70% or more overlap or username contained in password).
    Returns True if too similar, False otherwise.
    """
    username_set = set(username.lower()) # Convert username to lowercase and create a set of unique characters
    password_set = set(password.lower()) # Convert password to lowercase and create a set of unique characters
    overlap = username_set & password_set # Find the intersection of characters between username and password
    return len(overlap) / len(username_set) >= 0.7 or username.lower() in password.lower() # Check if the overlap is 70% or more, or if the username is contained in the password

def is_password_valid(username, password): # This function checks if the password meets the specified criteria, including length, character requirements, and similarity to the username. It returns an error message if the password is invalid, or None if it is valid.
    """
    Validate the password based on length, character requirements, and similarity to username.
    Returns an error message string if invalid, or None if valid.
    """
    if len(password) < 8: # Check if the password is at least 8 characters long
        return "Password must be at least 8 characters long"
    if " " in password: # Check if the password contains spaces
        return "Password must not contain spaces"
    if not any(char.isupper() for char in password): # Check if the password contains at least one uppercase letter
        return "Password must include an uppercase letter"
    if not any(char.isdigit() for char in password): # Check if the password contains at least one number
        return "Password must include a number"
    if password == username: # Check if the password is the same as the username
        return "Password cannot be the same as username"
    if is_password_similar(username, password): # Check if the password is too similar to the username
        return "Password is too similar to the username"
    return None


# -------------------------------------------------------------
# GUI navigation utility
# -------------------------------------------------------------
def open_login():
    """
    Launch the login page in a new Python process.
    """
    subprocess.Popen([sys.executable, LOGIN_PAGE])

# -------------------------------------------------------------
# Success window utility
# -------------------------------------------------------------
def open_success_window():
    """
    Open a new window to show signup success message.
    """
    success_window = Toplevel(app)
    success_window.title("Success")
    success_window.geometry("300x150")
    Label(success_window, text="Signup Successful!", font=("Arial", 14)).pack(expand=True)
    Button(success_window, text="OK", command=success_window.destroy).pack(pady=10)


# -------------------------------------------------------------
# User management: sorted insertion and file rewrite
# -------------------------------------------------------------
def save_user(username, password):
    """
    Save the new user to the CSV file.
    Reads all existing records, inserts the new user, sorts alphabetically (case-insensitive),
    and rewrites the file with the updated sorted data.
    Uses insertion sort for clarity and maintainability.
    """
    # Read existing records
    records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="") as file:
            reader = csv.DictReader(file)
            records = [(row.get("username", ""), row.get("password", "")) for row in reader]

    # Insert new record
    records.append((username, password))

    # Insertion sort (case-insensitive by username)
    for i in range(1, len(records)):
        key_item = records[i]
        j = i - 1
        while j >= 0 and records[j][0].lower() > key_item[0].lower():
            records[j + 1] = records[j]
            j -= 1
        records[j + 1] = key_item

    # Rewrite file with header and sorted records
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["username", "password"])
        for u, p in records:
            writer.writerow([u, p])


# -------------------------------------------------------------
# GUI signup handler
# -------------------------------------------------------------
def signup():
    """
    Handle the signup process when the user clicks the signup button.
    Validates username and password, checks for matching passwords,
    inserts the new user in sorted order, and rewrites the CSV.
    Provides meaningful error messages for all validation failures.
    """
    # Clear previous error messages and reset color
    error_text.set("")
    if error_label:
        error_label.config(fg=error_fg)

    # Read values from tkinter variables
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    confirm = confirm_entry.get().strip()

    # Basic validations
    username_error = is_username_valid(username)
    if username_error:
        error_text.set(username_error)
        if error_label:
            error_label.config(fg="red")
        return

    if password != confirm: # Check if password and confirm password match
        error_text.set("Passwords do not match")
        if error_label:
            error_label.config(fg="red")
        return

    password_error = is_password_valid(username, password) # Validate password with respect to username and criteria
    if password_error:
        error_text.set(password_error)
        if error_label:
            error_label.config(fg="red")
        return

    save_user(username, password) # Save the new user to the CSV file (in sorted order)
    error_text.set("Signup successful!")
    if error_label:
        error_label.config(fg="green")

    open_success_window()


# -------------------------------------------------------------
# Main program app interface (Tkinter GUI setup)
# -------------------------------------------------------------
create_csv_if_missing()  # Ensure the CSV file exists before starting the app

app = Tk()
app.title("Signup Page")
app.geometry("800x300")

# Create tkinter variables AFTER the main Tk root exists
username_entry = StringVar()
password_entry = StringVar()
confirm_entry = StringVar()
error_fg = "red"

# Build the UI using Label (not Text) for labels
Label(app, text="Username:").pack()
Entry(app, textvariable=username_entry).pack()

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