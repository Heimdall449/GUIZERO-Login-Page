from tkinter import *
import csv
import os
import re

"configuration"

CSV_FILE = "GUIZERO-Login-Page/users.csv"

# tkinter variable placeholders (will be initialized after `Tk()` exists)
username_entry = None
password_entry = None
confirm_entry = None
error_text = None
error_label = None
error_fg = "red"


"utility functions"

#-----------------create csv file if csv file doesn't exist---------------------

def create_csv_if_missing(): # Create the CSV file with headers if it doesn't exist
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password"])

#-----------------username validation functions---------------------

def username_exists(username): # Check if the username already exists in the CSV file
    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)
        return any(row["username"] == username for row in reader)
    
def is_username_valid(username): # Validate the username based on length, allowed characters, and uniqueness
    if not 5 <= len(username) <= 20:
        return "Username must be 5–20 characters long"
    if not re.match(r"^\w+$", username):
        return "Username can only contain letters, numbers, and underscores"
    if username_exists(username):
        return "Username already exists"
    return None

#-----------------password validation functions--------------------

def is_password_similar(username, password): # Check if the password is too similar to the username (50% or more overlap or username contained in password)
    username_set = set(username.lower())
    password_set = set(password.lower())
    overlap = username_set & password_set
    return len(overlap) / len(username_set) >= 0.7 or username.lower() in password.lower() # determines how similar the password can be to the username to be recognised as an invalid password/username

def is_password_valid(username, password): # Validate the password based on length, character requirements, and similarity to username
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if " " in password:
        return "Password must not contain spaces"
    if not any(char.isupper() for char in password):
        return "Password must include an uppercase letter"
    if not any(char.isdigit() for char in password):
        return "Password must include a number"
    if password == username:
        return "Password cannot be the same as username"
    if is_password_similar(username, password):
        return "Password is too similar to the username"
    return None

def open_success_window():
    success_window = Toplevel(app)
    success_window.title("Success")
    success_window.geometry("300x150")

    Label(success_window, text="Signup Successful!", font=("Arial", 14)).pack(expand=True)

    Button(success_window, text="OK", command=success_window.destroy).pack(pady=10)

#-----------------user management functions---------------------

def save_user(username, password): # Save the new user to the CSV file
    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, password])

#-----------------GUI functions---------------------

def signup(): # Handle the signup process when the user clicks the signup button
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

    if password != confirm:
        error_text.set("Passwords do not match")
        if error_label:
            error_label.config(fg="red")
        return

    password_error = is_password_valid(username, password)
    if password_error:
        error_text.set(password_error)
        if error_label:
            error_label.config(fg="red")
        return

    save_user(username, password)
    error_text.set("Signup successful!")
    if error_label:
        error_label.config(fg="green")

    open_success_window()

#-----------------main program app interface---------------------
create_csv_if_missing() # Ensure the CSV file exists before starting the app

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

# Label bound to `error_text`; we'll adjust its fg in `signup()` as needed
error_text = StringVar() # Initialize the error_text variable
error_label = Label(app, textvariable=error_text, fg=error_fg)
error_label.pack()

app.mainloop()