
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

# make sure parent directory (contains User.py) is importable
_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(_script_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from User import User, is_password_valid


"configuration"

# --- Configuration ---
_csv_dir = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(_csv_dir, "users.csv")  # Path to user data CSV
SIGNUP_PAGE = os.path.join(_csv_dir, "signup.py")  # Path to signup page

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
    Load user records from CSV and return a list of :class:`User` objects sorted by username.
    If the CSV does not exist, return an empty list.
    """
    if not os.path.exists(CSV_FILE):
        return []
    records = []
    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            user = User(
                username=row.get("username", ""),
                password=row.get("password", ""),
                name=row.get("name", ""),
                age=row.get("age", ""),
                email=row.get("email", ""),
                form=row.get("form", ""),
                subjects=row.get("subjects", ""),
            )
            records.append(user)
    records.sort(key=lambda u: u.username.lower())
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
    usernames = [u.username for u in records]
    return binary_search_usernames(usernames, username)



def open_success_window(user: User):
    """
    Display a window listing the full user data and offering password change.
    """
    success_window = Toplevel(app)
    success_window.title("User Data")
    success_window.geometry("400x300")
    Label(success_window, text="Login Successful", font=("Arial", 14)).pack(pady=5)
    Label(success_window, text=user.display_data(), justify=LEFT).pack(pady=10)
    Button(success_window, text="Change Password", command=lambda: PasswordChangeWindow(success_window, user)).pack(pady=5)
    Button(success_window, text="OK", command=success_window.destroy).pack(pady=5)



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
    Uses binary search against the list of users, then checks password.
    """
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

    idx = find_user_index(username)
    if idx == -1:
        error_text.set("Username not found")
        if error_label:
            error_label.config(fg="red")
        return

    records = load_user_records()
    user = records[idx]
    if password == user.password:
        error_text.set("")
        if error_label:
            error_label.config(fg="green")
        open_success_window(user)
    else:
        error_text.set("Incorrect password")
        if error_label:
            error_label.config(fg="red")



# -------------------------------------------------------------
# Additional dialogs

class PasswordChangeWindow(Toplevel):
    """Dialog window for changing a user's password."""
    
    def __init__(self, parent, user: User):
        """
        Initialize the password change dialog.
        
        Args:
            parent: The parent tkinter window
            user: The User object whose password will be changed
        """
        super().__init__(parent)
        self.user = user
        self.title("Change Password")
        self.geometry("320x200")
        
        # New password label and entry
        Label(self, text="New password:").pack()
        self.new_var = StringVar()
        Entry(self, textvariable=self.new_var, show="*").pack()
        
        # Confirm password label and entry
        Label(self, text="Confirm password:").pack()
        self.confirm_var = StringVar()
        Entry(self, textvariable=self.confirm_var, show="*").pack()
        
        # Message label for feedback
        self.msg = StringVar()
        Label(self, textvariable=self.msg, fg="red").pack(pady=5)
        
        # Submit button
        Button(self, text="Submit", command=self.submit).pack(pady=5)
    
    def submit(self):
        """Handle password change submission and validation."""
        new = self.new_var.get().strip()
        conf = self.confirm_var.get().strip()
        
        # Check if passwords match
        if new != conf:
            self.msg.set("Passwords do not match")
            return
        
        # Validate password
        err = is_password_valid(self.user.username, new)
        if err:
            self.msg.set(err)
            return
        
        # Update password in CSV
        self.user.change_password(new, CSV_FILE)
        self.msg.set("Password updated")

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
# The password entry field uses the `show="*"` option to mask the input, providing a more secure way for users to enter their passwords without displaying them on the screen.
Label(app, text="Password:").pack()
Entry(app, textvariable=password_entry, show="*").pack()

Button(app, text="Log In", command=login).pack(pady=8) # Login button triggers the login function when clicked
Button(app, text="Sign Up", command=open_signup).pack() # Sign Up button opens the signup page when clicked

# Error message label
error_text = StringVar()
error_label = Label(app, textvariable=error_text, fg=error_fg)
error_label.pack(pady=8)

# Start the GUI event loop
app.mainloop()
