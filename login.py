
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
import difflib  # used for similarity checks between passwords

# make sure parent directory (contains User.py) is importable
_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(_script_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from User import User, is_password_valid


"configuration to define paths to CSV and signup page"

# --- Configuration ---
_csv_dir = os.path.dirname(os.path.abspath(__file__)) # directory of this script
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
        with open(self.csv_path, newline="") as file: # open the CSV file for reading
            reader = csv.DictReader(file) # read CSV rows as dictionaries
            for row in reader: # create User objects from CSV rows, using get() to avoid KeyErrors if fields are missing
                user = User(
                    username=row.get("username", ""),
                    password=row.get("password", ""),
                    name=row.get("name", ""),
                    age=row.get("age", ""),
                    email=row.get("email", ""),
                    form=row.get("form", ""),
                    subjects=row.get("subjects", ""),
                )
                records.append(user) # sort records by username for binary search
        records.sort(key=lambda u: u.username.lower())
        return records
    
    @staticmethod
    def binary_search_usernames(usernames, target): # helper method for binary search
        """
        Perform binary search on sorted list of usernames to find target username.
        Returns the index of target in usernames, or -1 when not found.
        Binary search is O(log n) and requires sorted input.
        Comparison is case-insensitive.
        """
        lo = 0
        hi = len(usernames) - 1 # binary search on the list of usernames
        target_l = target.lower()
        while lo <= hi:
            mid = (lo + hi) // 2
            mid_val = usernames[mid].lower() # case-insensitive comparison
            if mid_val == target_l: # found the target username
                return mid # return the index of the found username
            elif mid_val < target_l: # target is after mid
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
        idx = self.find_user_index(username) # find the index of the username using binary search
        if idx == -1: 
            return None # username not found
        records = self.load_records()
        return records[idx] # return the User object at the found index



# -------------------------------------------------------------
# Window classes for login UI
# -------------------------------------------------------------
class PasswordChangeWindow(Toplevel):
    """Dialog used for resetting a forgotten/old password.  

    This window is launched from the login screen (and optionally from the
    success dialog) and asks the user to provide their username, email and
    last-known password.  Only when the entered old-password has at least
    60% similarity to the stored one is the "new password" field enabled.
    After a successful change a small confirmation window allows the user to
    return to the login page.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reset Password")
        self.geometry("360x300")

        # repository to look up users
        self.repo = UserRepository(CSV_FILE)

        # variables for all four entry fields
        self.username_var = StringVar()
        self.email_var = StringVar()
        self.old_var = StringVar()
        self.new_var = StringVar()
        self.msg = StringVar()

        # build inputs
        Label(self, text="Username:").pack()
        Entry(self, textvariable=self.username_var).pack()

        Label(self, text="Email:").pack()
        Entry(self, textvariable=self.email_var).pack()

        Label(self, text="Last known password:").pack()
        Entry(self, textvariable=self.old_var, show="*").pack()

        Label(self, text="New password:").pack()
        self.new_entry = Entry(self, textvariable=self.new_var, show="*", state="disabled")
        self.new_entry.pack()

        Label(self, textvariable=self.msg, fg="red").pack(pady=5) # message label for feedback on similarity and validation
        self.confirm_btn = Button(self, text="Confirm", command=self.confirm, state="disabled") # confirm button is disabled until similarity check passes
        self.confirm_btn.pack(pady=5) # pack the confirm button below the message label

        # update enabled state whenever username or old password changes
        self.username_var.trace_add("write", lambda *args: self._check_similarity())
        self.old_var.trace_add("write", lambda *args: self._check_similarity())

    def _check_similarity(self):
        # clear previous message
        self.msg.set("")
        uname = self.username_var.get().strip()
        if not uname: # if username field is empty, disable new password input and show message
            self.new_entry.config(state="disabled")
            self.confirm_btn.config(state="disabled")
            return
        user = self.repo.find_user(uname)
        if user is None: # if username not found, disable new password input and show message
            self.msg.set("Username not found")
            self.new_entry.config(state="disabled")
            self.confirm_btn.config(state="disabled")
            return
        old_input = self.old_var.get()
        if not old_input: # if old password field is empty, disable new password input
            self.new_entry.config(state="disabled")
            self.confirm_btn.config(state="disabled")
            return
        ratio = difflib.SequenceMatcher(None, old_input, user.password).ratio() # calculate similarity ratio
        if ratio >= 0.6:
            self.msg.set("Old password looks familiar – enter a new password")
            self.new_entry.config(state="normal")
            self.confirm_btn.config(state="normal")
        else:
            self.msg.set("Old password not similar enough")
            self.new_entry.config(state="disabled")
            self.confirm_btn.config(state="disabled")

    def confirm(self):
        uname = self.username_var.get().strip()
        email = self.email_var.get().strip()
        new_pw = self.new_var.get().strip()
        user = self.repo.find_user(uname)
        if user is None:
            self.msg.set("Username not found")
            return
        if email.lower() != user.email.lower():
            self.msg.set("Email does not match")
            return
        err = is_password_valid(uname, new_pw)
        if err:
            self.msg.set(err)
            return
        user.change_password(new_pw, CSV_FILE)
        SuccessResetWindow(self)


class SuccessResetWindow(Toplevel):
    """Simple confirmation dialog displayed after a password reset."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Success")
        self.geometry("300x150")
        Label(self, text="Password change successful!").pack(pady=10)
        Button(self, text="Return to login", command=self._return).pack(pady=5)

    def _return(self):
        # close the reset window (parent of this) then this dialog
        try:
            self.master.destroy()
        except Exception:
            pass
        self.destroy()


class SuccessWindow(Toplevel):
    """Dialog window displayed after successful login."""
    
    def __init__(self, parent, user: User):
        super().__init__(parent)
        self.user = user
        self.title("User Data")
        self.geometry("400x300")
        
        Label(self, text="Login Successful", font=("Arial", 14)).pack(pady=5)
        # Display user data without the password
        user_info = user.display_data().replace(f"Password: {user.password}\n", "")
        Label(self, text=user_info, justify=LEFT).pack(pady=10)
        # allow the user to re‑open the reset form if they wish
        Button(self, text="Change Password", command=self._open_password_change).pack(pady=5)
        Button(self, text="OK", command=self.destroy).pack(pady=5)
    
    def _open_password_change(self):
        """Open the password reset dialog (same as from login page)."""
        PasswordChangeWindow(self)


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

        # new password reset button sits under the password box
        Button(self, text="Change Password", command=self.open_password_reset).pack(pady=2)
        
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

    def open_password_reset(self):
        """Show the password reset dialog from the login screen."""
        PasswordChangeWindow(self)


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
