import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
from datetime import datetime

class RegistrationForm(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Registration Form")
        self.geometry("400x500")
        self.configure(background='#f0f0f0')  # Setting background color

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg='#f0f0f0')
        main_frame.pack(expand=True, fill=tk.BOTH)

        label_heading = tk.Label(main_frame, text="User Registration", font=("Helvetica", 18, "bold"), bg='#f0f0f0')
        label_heading.pack(pady=10)

        form_frame = tk.Frame(main_frame, bg='#f0f0f0')
        form_frame.pack(padx=20, pady=10, anchor='center')

        # Full Name
        self.label_fullname = tk.Label(form_frame, text="Full Name:", bg='#f0f0f0')
        self.label_fullname.grid(row=0, column=0, sticky='w', pady=5)
        self.entry_fullname = tk.Entry(form_frame)
        self.entry_fullname.grid(row=0, column=1, pady=5)

        # Username
        self.label_username = tk.Label(form_frame, text="Username:", bg='#f0f0f0')
        self.label_username.grid(row=1, column=0, sticky='w', pady=5)
        self.entry_username = tk.Entry(form_frame)
        self.entry_username.grid(row=1, column=1, pady=5)

        # Password
        self.label_password = tk.Label(form_frame, text="Password:", bg='#f0f0f0')
        self.label_password.grid(row=2, column=0, sticky='w', pady=5)
        self.entry_password = tk.Entry(form_frame, show='*')
        self.entry_password.grid(row=2, column=1, pady=5)

        # Date of Birth
        self.label_dob = tk.Label(form_frame, text="Date of Birth:", bg='#f0f0f0')
        self.label_dob.grid(row=3, column=0, sticky='w', pady=5)
        self.dob_frame = tk.Frame(form_frame, bg='#f0f0f0')
        self.dob_frame.grid(row=3, column=1, pady=5)
        self.dob_day = ttk.Combobox(self.dob_frame, values=list(range(1, 32)))
        self.dob_day.grid(row=0, column=0)
        self.dob_day.set("Day")
        self.dob_month = ttk.Combobox(self.dob_frame, values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        self.dob_month.grid(row=0, column=1)
        self.dob_month.set("Month")
        self.dob_year = ttk.Combobox(self.dob_frame, values=list(range(1900, 2023)))
        self.dob_year.grid(row=0, column=2)
        self.dob_year.set("Year")

        # Location
        self.label_location = tk.Label(form_frame, text="Location:", bg='#f0f0f0')
        self.label_location.grid(row=4, column=0, sticky='w', pady=5)
        self.entry_location = tk.Entry(form_frame)
        self.entry_location.grid(row=4, column=1, pady=5)

        # Register Button
        self.btn_register = tk.Button(form_frame, text="Register", command=self.register)
        self.btn_register.grid(row=7, columnspan=2, pady=10)

    def register(self):
        fullname = self.entry_fullname.get()
        username = self.entry_username.get()
        password = self.entry_password.get()
        dob_day = self.dob_day.get()
        dob_month = self.dob_month.get()
        dob_year = self.dob_year.get()
        location = self.entry_location.get()
        city = self.entry_city.get()
        courses = self.selected_courses.get()

        # Validate input
        if not all([fullname, username, password, dob_day, dob_month, dob_year, location, city, courses]):
            messagebox.showerror("Error", "Please fill out all fields")
            return

        dob = f"{dob_day} {dob_month} {dob_year}"

        # Store registration data in JSON file
        data = {
            "Full Name": fullname,
            "Username": username,
            "Password": password,
            "Date of Birth": dob,
            "Location": location,
            "City": city,
            "Courses": courses
        }

        with open("registration_details.json", "w") as file:
            json.dump(data, file, indent=4)

        # Confirmation message
        messagebox.showinfo("Registration Successful", "Registration details saved successfully!")

if __name__ == "__main__":
    app = RegistrationForm()

















    app.mainloop()
