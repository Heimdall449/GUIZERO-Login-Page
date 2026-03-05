
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


"repository and utility classes"

# -------------------------------------------------------------
# User data repository with binary search utilities
# -------------------------------------------------------------
class UserRepository:
    """Handles loading and searching user records from CSV."""
    
    def __init__(self, csv_path):
        """Initialize repository with path to CSV file."""
        self.csv_path = csv_path
    
    def load_records(self):
        """
        Load user records from CSV and return a list of User objects sorted by username.
        Returns an empty list if the CSV does not exist.
        """
        if not os.path.exists(self.csv_path):
            return []
        records = []
        with open(self.csv_path, newline="") as file:
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
    
    @staticmethod
    def binary_search_usernames(usernames, target):
        """
        Perform binary search on sorted list of usernames to find target username.
        Returns the index of target in usernames, or -1 when not found.
        Binary search is O(log n) and requires sorted input.
        Comparison is case-insensitive.
        """
        lo = 0
        hi = len(usernames) - 1
        target_l = target.lower()
        while lo <= hi:
            mid = (lo + hi) // 2
            mid_val = usernames[mid].lower()
            if mid_val == target_l:
                return mid
            elif mid_val < target_l:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1
    
    def find_user_index(self, username):
        """
        Return index of username in CSV (using binary search) or -1 if not found.
        """
        records = self.load_records()
        usernames = [u.username for u in records]
        return self.binary_search_usernames(usernames, username)
    
    def find_user(self, username):
        """Find and return a User object by username, or None if not found."""
        idx = self.find_user_index(username)
        if idx == -1:
            return None
        records = self.load_records()
        return records[idx]



# -------------------------------------------------------------
# Window classes for login UI
# -------------------------------------------------------------
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


class SuccessWindow(Toplevel):
    """Dialog window displayed after successful login."""
    
    def __init__(self, parent, user: User):
        """
        Initialize the success window with user data.
        
        Args:
            parent: The parent tkinter window
            user: The User object whose data will be displayed
        """
        super().__init__(parent)
        self.user = user
        self.title("User Data")
        self.geometry("400x300")
        
        Label(self, text="Login Successful", font=("Arial", 14)).pack(pady=5)
        Label(self, text=user.display_data(), justify=LEFT).pack(pady=10)
        Button(self, text="Change Password", command=self._open_password_change).pack(pady=5)
        Button(self, text="OK", command=self.destroy).pack(pady=5)
    
    def _open_password_change(self):
        """Open the password change dialog."""
        PasswordChangeWindow(self, self.user)


class LoginWindow(Tk):
    """Main login window with binary search authentication."""
    
    def __init__(self, csv_file=CSV_FILE, signup_page=SIGNUP_PAGE):
        """
        Initialize the login window.
        
        Args:
            csv_file: Path to the users CSV file
            signup_page: Path to the signup.py script
        """
        super().__init__()
        self.csv_file = csv_file
        self.signup_page = signup_page
        self.repository = UserRepository(csv_file)
        
        self.title("Login Page")
        self.geometry("400x220")
        
        # Create tkinter variables
        self.username_entry = StringVar()
        self.password_entry = StringVar()
        self.error_text = StringVar()
        
        self._build_ui()
    
    def _build_ui(self):
        """Construct the login UI."""
        Label(self, text="Username:").pack()
        Entry(self, textvariable=self.username_entry).pack()
        
        Label(self, text="Password:").pack()
        Entry(self, textvariable=self.password_entry, show="*").pack()
        
        Button(self, text="Log In", command=self.login).pack(pady=8)
        Button(self, text="Sign Up", command=self.open_signup).pack()
        
        # Error message label
        self.error_label = Label(self, textvariable=self.error_text, fg="red")
        self.error_label.pack(pady=8)
    
    def login(self):
        """Handle the login process when the user clicks the login button."""
        self.error_text.set("")
        self.error_label.config(fg="red")
        
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.error_text.set("Please enter both username and password")
            return
        
        user = self.repository.find_user(username)
        if user is None:
            self.error_text.set("Username not found")
            return
        
        if password == user.password:
            self.error_text.set("")
            self.error_label.config(fg="green")
            SuccessWindow(self, user)
        else:
            self.error_text.set("Incorrect password")
    
    def open_signup(self):
        """Launch the signup page in a new Python process."""
        subprocess.Popen([sys.executable, self.signup_page])


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
