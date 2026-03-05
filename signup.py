
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
_script_dir = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(_script_dir, "users.csv")
LOGIN_PAGE = os.path.join(_script_dir, "login.py")


"repository and utility classes"

# -------------------------------------------------------------
# User data repository for signup
# -------------------------------------------------------------
class UserRepository:
    """Handles saving and managing user records in CSV."""
    
    def __init__(self, csv_path):
        """Initialize repository with path to CSV file."""
        self.csv_path = csv_path
    
    def create_csv_if_missing(self):
        """Create CSV with header if it doesn't exist."""
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
    
    def save_user(self, username, password, name='', age='', email='', form='', subjects=''):
        """
        Append new user then rewrite CSV sorted by username.
        
        Args:
            username: User's username
            password: User's password
            name: User's name
            age: User's age
            email: User's email
            form: User's form/grade
            subjects: User's subjects (comma-separated)
        """
        records = []
        if os.path.exists(self.csv_path):
            with open(self.csv_path, newline='', encoding='utf-8') as f:
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
        
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(records)


"window classes"

# -------------------------------------------------------------
# Window classes for signup UI
# -------------------------------------------------------------
class SuccessWindow(Toplevel):
    """Dialog window displayed after successful signup."""
    
    def __init__(self, parent):
        """
        Initialize the success window.
        
        Args:
            parent: The parent tkinter window
        """
        super().__init__(parent)
        self.title("Success")
        self.geometry("300x120")
        Label(self, text="Signup Successful!", font=("Arial", 14)).pack(expand=True)
        Button(self, text="OK", command=self.destroy).pack(pady=8)


class SignupWindow(Tk):
    """Main signup window with form validation."""
    
    def __init__(self, csv_file=CSV_FILE, login_page=LOGIN_PAGE):
        """
        Initialize the signup window.
        
        Args:
            csv_file: Path to the users CSV file
            login_page: Path to the login.py script
        """
        super().__init__()
        self.csv_file = csv_file
        self.login_page = login_page
        self.repository = UserRepository(csv_file)
        self.repository.create_csv_if_missing()
        
        self.title("Signup Page")
        self.geometry("800x300")
        
        # Create tkinter variables
        self.username_entry = StringVar()
        self.name_entry = StringVar()
        self.age_entry = StringVar()
        self.email_entry = StringVar()
        self.form_entry = StringVar()
        self.subjects_entry = StringVar()
        self.password_entry = StringVar()
        self.confirm_entry = StringVar()
        self.error_text = StringVar()
        
        self._build_ui()
    
    def _build_ui(self):
        """Construct the signup UI."""
        Label(self, text="Username:").pack()
        Entry(self, textvariable=self.username_entry).pack()
        
        Label(self, text="Name:").pack()
        Entry(self, textvariable=self.name_entry).pack()
        
        Label(self, text="Email:").pack()
        Entry(self, textvariable=self.email_entry).pack()
        
        Label(self, text="Age:").pack()
        Entry(self, textvariable=self.age_entry).pack()
        
        Label(self, text="Form:").pack()
        Entry(self, textvariable=self.form_entry).pack()
        
        Label(self, text="Subjects (comma-separated):").pack()
        Entry(self, textvariable=self.subjects_entry).pack()
        
        Label(self, text="Password:").pack()
        Entry(self, textvariable=self.password_entry, show="*").pack()
        
        Label(self, text="Confirm Password:").pack()
        Entry(self, textvariable=self.confirm_entry, show="*").pack()
        
        Button(self, text="Sign Up", command=self.signup).pack()
        Button(self, text="Log In", command=self.open_login).pack()
        
        # Error message label
        self.error_label = Label(self, textvariable=self.error_text, fg="red")
        self.error_label.pack()
    
    def signup(self):
        """Handle signup: validate fields and save new user."""
        self.error_text.set("")
        self.error_label.config(fg="red")
        
        username = self.username_entry.get().strip()
        name_val = self.name_entry.get().strip()
        age_val = self.age_entry.get().strip()
        email = self.email_entry.get().strip()
        form_val = self.form_entry.get().strip()
        subjects_val = self.subjects_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        
        # Validate username
        username_error = is_username_valid(username)
        if username_error:
            self.error_text.set(username_error)
            return
        
        # Validate name
        if not is_name_valid(name_val):
            self.error_text.set("Name can only contain letters and spaces")
            return
        
        # Validate age
        if not is_age_valid(age_val):
            self.error_text.set("Age must be a positive integer less than 150")
            return
        
        # Validate email
        if not is_email_valid(email):
            self.error_text.set("Invalid email format")
            return
        
        # Validate form
        if not is_form_valid(form_val):
            self.error_text.set("Form must be e.g. 12A or 9")
            return
        
        # Validate subjects
        if not is_subjects_valid(subjects_val):
            self.error_text.set("Subjects must be comma-separated words")
            return
        
        # Check passwords match
        if password != confirm:
            self.error_text.set("Passwords do not match")
            return
        
        # Validate password
        pw_err = is_password_valid(username, password)
        if pw_err:
            self.error_text.set(pw_err)
            return
        
        # Save user
        self.repository.save_user(username, password, name_val, age_val, email, form_val, subjects_val)
        self.error_text.set("Signup successful!")
        self.error_label.config(fg="green")
        SuccessWindow(self)
    
    def open_login(self):
        """Launch the login page in a new Python process."""
        subprocess.Popen([sys.executable, self.login_page])


if __name__ == "__main__":
    app = SignupWindow()
    app.mainloop()

