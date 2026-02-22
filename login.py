
# -------------------------------------------------------------
# GUIZERO-Login-Page/login.py
# Login system with binary search and sorted user data
# -------------------------------------------------------------
# This file implements a login GUI using tkinter. It loads user credentials
# from a CSV file, uses binary search to efficiently check for username existence,
# and validates passwords. Error handling and user feedback are provided.
# -------------------------------------------------------------

" Imports "
from tkinter import *
import csv
import os
import subprocess
import sys


"configuration"

# --- Configuration ---
_script_dir = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(_script_dir, "users.csv")  # Path to user data CSV
SIGNUP_PAGE = os.path.join(_script_dir, "signup.py")  # Path to signup page

# tkinter variable placeholders (will be initialized after `Tk()` exists)

# Tkinter variable placeholders (initialized after Tk() exists)
username_entry = None
password_entry = None
error_text = None
error_label = None
error_fg = "red"


"utility functions"

# -------------------------------------------------------------
# User data loading and search utilities
# -------------------------------------------------------------
def load_user_records():
    """
    Load user records from CSV and return a list of (username, password) tuples sorted by username.
    If the CSV does not exist, return an empty list.
    Sorting is case-insensitive for consistent binary search.
    """
    if not os.path.exists(CSV_FILE): # If the CSV file does not exist, return an empty list
        return []
    with open(CSV_FILE, newline="") as file: # Open the CSV file for reading
        reader = csv.DictReader(file)
        records = [(row.get("username", ""), row.get("password", "")) for row in reader] # Read each row and create a list of (username, password) tuples, using empty strings as defaults if keys are missing
    # Ensure sorted order by username (stable, case-insensitive)
    records.sort(key=lambda t: t[0].lower()) # Sort the records by username in a case-insensitive manner to ensure binary search works correctly
    return records



def binary_search_usernames(usernames, target): # This function performs a binary search on a sorted list of usernames to find the index of the target username. It compares usernames in a case-insensitive manner to ensure that the search is not affected by letter case. If the target username is found, it returns its index; otherwise, it returns -1 to indicate that the username was not found in the list.
    """
    Perform binary search on sorted list of usernames to find target username.
    Returns the index of target in usernames, or -1 when not found.
    Binary search is O(log n) and requires sorted input.
    """
    lo = 0
    hi = len(usernames) - 1
    target_l = target.lower()
    while lo <= hi:
        mid = (lo + hi) // 2
        mid_val = usernames[mid].lower()  # Compare in lowercase for case-insensitive search
        if mid_val == target_l:
            return mid
        elif mid_val < target_l:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
# assumes usernames are sorted in a case-insensitive manner for correct binary search functionality


def find_user_index(username):
    """
    Return index of username in CSV (using binary search) or -1 if not found.
    Loads sorted records, extracts usernames, and searches.
    """
    records = load_user_records()
    usernames = [u for (u, p) in records]
    return binary_search_usernames(usernames, username)



def open_success_window(username):
    """
    Open a new window to show login success message with the username.
    """
    success_window = Toplevel(app)
    success_window.title("Login Successful")
    success_window.geometry("320x120")
    Label(success_window, text=f"Welcome, {username}!", font=("Arial", 14)).pack(expand=True)
    Button(success_window, text="OK", command=success_window.destroy).pack(pady=10)



def open_signup():
    """
    Launch the signup page in a new Python process.
    """
    subprocess.Popen([sys.executable, SIGNUP_PAGE])



# -------------------------------------------------------------
# GUI login handler
# -------------------------------------------------------------
def login():
    """
    Handle the login process when the user clicks the login button.
    Uses binary search to check username existence and validates password.
    Provides meaningful error messages for empty fields, username not found, and incorrect password.
    """
    error_text.set("")  # Clear previous error messages
    if error_label:
        error_label.config(fg=error_fg)

    username = username_entry.get().strip()
    password = password_entry.get().strip()

    # Error: empty input fields
    if not username or not password:
        error_text.set("Please enter both username and password")
        if error_label:
            error_label.config(fg="red")
        return

    # Use binary search to find username quickly in the sorted records
    idx = find_user_index(username)
    if idx == -1:
        error_text.set("Username not found")
        if error_label:
            error_label.config(fg="red")
        return

    # Load password for found user and validate
    records = load_user_records()
    found_username, found_password = records[idx]
    if password == found_password:
        error_text.set("")
        if error_label:
            error_label.config(fg="green")
        open_success_window(username)
    else:
        error_text.set("Incorrect password")
        if error_label:
            error_label.config(fg="red")



# -------------------------------------------------------------
# Main program app interface (Tkinter GUI setup)
# -------------------------------------------------------------
app = Tk()
app.title("Login Page")
app.geometry("400x220")

# Create tkinter variables AFTER the main Tk root exists
username_entry = StringVar()
password_entry = StringVar()
error_fg = "red"

# Build the UI
Label(app, text="Username:").pack()
Entry(app, textvariable=username_entry).pack()

Label(app, text="Password:").pack()
Entry(app, textvariable=password_entry, show="*").pack()

Button(app, text="Log In", command=login).pack(pady=8)
Button(app, text="Sign Up", command=open_signup).pack()

# Error message label
error_text = StringVar()
error_label = Label(app, textvariable=error_text, fg=error_fg)
error_label.pack(pady=8)

# Start the GUI event loop
app.mainloop()
