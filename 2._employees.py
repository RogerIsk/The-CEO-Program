from email_validator import validate_email, EmailNotValidError #used to check if email addresses are correctly formatted and valid.
import re #The re module is used for pattern matching and string manipulation.
import pandas as pd #is used to manage and manipulate large datasets efficiently.
import customtkinter as ctk #is used to create graphical user interfaces,
from tkinter import ttk #is used to automate tasks in web browsers, such as scraping web pages or testing web applications.
import tkinter as tk #allows the program to copy and paste text to and from the system clipboard.
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import datetime
import os
import threading
import subprocess


# Function to initialize WebDriver
def initialize_driver():
    def start_chrome_driver(result):                                                                       # Starting with Chrome running in headless mode
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            result.append(webdriver.Chrome(options=chrome_options))
        except Exception as e:
            result.append(e)

    def start_firefox_driver(result):                                                                      # Using Firefox if Chrome fails
        try:
            firefox_options = FirefoxOptions()
            firefox_options.headless = False
            firefox_options.add_argument("--headless")
            result.append(webdriver.Firefox(options=firefox_options))
        except Exception as e:
            result.append(e)
    
    # Timeout error handling
    result = []                 
    chrome_thread = threading.Thread(target=start_chrome_driver, args=(result,))
    chrome_thread.start()
    chrome_thread.join(timeout=3)                                                                           # Wait for 3 seconds between threads

    if chrome_thread.is_alive():
        print("Chrome WebDriver initialization timed out. Trying Firefox...")
        chrome_thread.join()                                                                                # Ensure the thread is cleaned up
        result.clear()
    else:
        if isinstance(result[0], Exception):
            print(f"Chrome WebDriver initialization failed: {result[0]}")
        else:
            print("Using Chrome WebDriver")
            return result[0]

    firefox_thread = threading.Thread(target=start_firefox_driver, args=(result,))
    firefox_thread.start()
    firefox_thread.join(timeout=3)                                                                          # Wait for 3 seconds

    if firefox_thread.is_alive():
        print("Firefox WebDriver initialization timed out.")
        firefox_thread.join()                                                                               # Ensure the thread is cleaned up
        raise RuntimeError("No suitable WebDriver found. Please ensure you have either geckodriver or chromedriver installed.")
    else:
        if isinstance(result[0], Exception):
            print(f"Firefox WebDriver initialization failed: {result[0]}")
            raise RuntimeError("No suitable WebDriver found. Please ensure you have either geckodriver or chromedriver installed.")
        else:
            print("Using Firefox WebDriver")
            return result[0]
        
def verify_email_smtp(email):
    try:
        # Basic email format validation
        if '@' not in email:
            return False, f"Invalid email format: {email}"
        
        # Perform email validation using email_validator
        is_valid = validate_email(email)
         
        if not is_valid:
            return False, f"Email is not valid: {email}"
        
        return True, "Email is valid"
        
    except EmailNotValidError as e:
        return False, f"Email validation error: {e}"
    except Exception as e:
        return False, f"Unexpected error during email validation: {e}"

# Testing the function verify_email_smtp
email = "example@example.com"
is_valid, info = verify_email_smtp(email)
print(f"Email {email} validation result: {is_valid}")
print(f"Additional information: {info}")

# Test with a valid email address
email = "aiolos129@gmail.com" 
is_valid, info = verify_email_smtp(email)
print(f"Email {email} validation result: {is_valid}")
print(f"Additional information: {info}")


# Function to scrape data from the main page
def scrape_main_page(driver, page_url):                                                                      
    driver.get(page_url)                                                                                    
    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-profileImage')))    # Tells the webdriver to wait till the CSS_Selector is loaded 
    profiles = driver.find_elements(By.CSS_SELECTOR, '.m-profileImage')                                     # Tells Selenium which element to target for scraping
    data = []                                                                                               
    for profile in profiles:                                                                                
        name = profile.find_element(By.CLASS_NAME, 'm-profileImage__name').text.strip()                     # Finding profile name
        job_title = profile.find_element(By.CLASS_NAME, 'm-profileImage__jobDescription').text.strip()      # Finding job description
        profile_link = profile.get_attribute('href')                                                        
        data.append({'Name': name, 'Job Title': job_title, 'Profile Link': profile_link})                   # Append found data to our list
    return data

# Function to scrape data from a profile page
def scrape_profile_page(driver, profile):
    if profile['Name'].startswith('Test User'):
        email = profile.get('Email')
        if email:
            is_valid, info = verify_email_smtp(email)
            profile['Email Valid'] = is_valid
            profile['Validation Info'] = info
            print(f"Test User Profile {profile['Name']} email validation result: {is_valid}, Info: {info}")
        else:
            print(f"Test user {profile['Name']} does not have an email.")
    else:
        profile_url = profile['Profile Link']
        driver.get(profile_url)

        email = None
        phone = None
        email_error = None
        phone_error = None

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'a-mailto')))
            email_elem = driver.find_element(By.CLASS_NAME, 'a-mailto')
            email = email_elem.get_attribute('href')
            if email.startswith("mailto:"):
                email = email.split(":")[1]
            else:
                email = email_elem.text.strip()
            
            # Validate the email
            is_valid, info = verify_email_smtp(email)
            profile['Email Valid'] = is_valid
            profile['Validation Info'] = info

            try:
                phone_elem = driver.find_element(By.XPATH, "//a[starts-with(@href, 'tel:')]")
                phone = phone_elem.get_attribute('href').split(":")[1]
            except Exception as e:
                phone_error = f"Error finding phone number for {profile['Name']}: {e}"

            profile.update({
                'Email': email if email else email_error,
                'Phone Number': phone if phone else phone_error
            })
            
        except Exception as e:
            email_error = f"finding email for {profile['Name']}: {e}"
            profile['Email'] = email_error

    return profile

# Function to export data to CSV file with a unique name
def export_to_csv(data):
    if not os.path.exists('employees files'):                                                               # Check for dir, if not create the directory for file storage                          
        os.makedirs('employees files')                                                                      
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")                                             # Adding a timestamp to the filename using strftime                   
    filename = os.path.join('employees files', f"profiles_{timestamp}.csv")                                 
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    messagebox.showinfo('Export Successful', f'Data exported to {filename}!')

# Function to update the GUI with scraped data
def update_gui(page_num=None):
    global profiles_data
    profiles_data = []

    test_profiles = [
        {'Name': 'Test User1', 'Job Title': 'Tester', 'Profile Link': 'https://example.com/profile1', 'Email': 'invalid-email', 'Phone Number': '1234567890'},
        {'Name': 'Test User2', 'Job Title': 'Tester', 'Profile Link': 'https://example.com/profile2', 'Email': 'invalid@domain', 'Phone Number': '1234567890'},
        {'Name': 'Test User3', 'Job Title': 'Tester', 'Profile Link': 'https://example.com/profile3', 'Email': 'valid@example.com', 'Phone Number': '1234567890'}
    ]
    profiles_data.extend(test_profiles)

    if page_num is None or page_num.strip() == "":
        page_numbers = range(1, 12)  # Gets pages 1-11 from the website if there's no input for page numbers
    else:
        try:
            page_numbers = [int(page_num)]
        except ValueError:
            messagebox.showwarning('Invalid Input', 'Please enter a valid page number.')
            return
    
    driver = initialize_driver()
    for num in page_numbers:
        print(f"Fetching data from page {num}")  # print statement to check if the program hangs fetching a certain page
        page_url = f"https://www.epunkt.com/team/p{num}"
        page_data = scrape_main_page(driver, page_url)  # Use a temporary list to store the current page data
        
        for profile in page_data:
            profile.update(scrape_profile_page(driver, profile))
        profiles_data += page_data  # Merge the current page data into the main profiles_data list

    for test_profile in test_profiles:  # Ensure test profiles are also validated and added
        scrape_profile_page(driver, test_profile)

    print("Data fetching complete")
    update_treeview()
    driver.quit()


# Function to update the Treeview with scraped data
def update_treeview():
    tree.delete(*tree.get_children())
    for i, profile in enumerate(profiles_data):
        email_text = profile['Email'] if profile['Email'] else 'Email not found'
        
        # Add a visual indicator for validated emails
        if profile.get('Email Valid', False):
            email_text += " ✔"  # Add a checkmark or any indicator
        
        values = (
            profile['Name'],
            profile['Job Title'],
            profile['Profile Link'],
            email_text,
            profile['Phone Number'] if profile['Phone Number'] else 'Phone number not found'
        )
        
        tree.insert('', 'end', values=values)
    
    tree.tag_configure('highlight', background='darkblue')

    # Configure tag for row highlighting
    print("Treeview update complete.")

# Function to export selected profiles to CSV file
def export_selected():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning('No Selection', 'Please select at least one profile to export.')
        return
    selected_profiles = []
    for item in selected_items:
        profile_id = item[1:]                                                                                # Remove the "I" prefix
        try:
            index = int(profile_id) - 1
            if 0 <= index < len(profiles_data):
                selected_profiles.append(profiles_data[index])
            else:
                print(f"Index {index} out of range. Skipping.")
        except ValueError:
            print(f"Cannot convert {profile_id} to integer. Skipping.")
    if selected_profiles:
        export_to_csv(selected_profiles)

# Function to export all profiles to CSV file
def export_all():
    export_to_csv(profiles_data)

# Function to copy selected profiles to clipboard
def copy_selected():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning('No Selection', 'Please select at least one profile to export.')
        return
    selected_profiles = []
    for item in selected_items:
        profile_id = item[1:]                                                                                # Remove the "I" prefix
        try:
            index = int(profile_id) - 1
            if 0 <= index < len(profiles_data):
                selected_profiles.append(profiles_data[index])
            else:
                print(f"Index {index} out of range. Skipping.")
        except ValueError:
            print(f"Cannot convert {profile_id} to integer. Skipping.")
    pyperclip.copy(str(selected_profiles))
    messagebox.showinfo('Copy Successful', 'Selected profiles copied to clipboard!')
    
# Function to delete selected profiles
def delete_selected():
    global profiles_data
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning('No Selection', 'Please select at least one profile to delete.')
        return
    
    selected_indices = []
    for item in selected_items:
        item_index = tree.index(item)                                                                        # Get the index of the selected item in the Treeview
        selected_indices.append(item_index)
    
    # Remove profiles from the profiles_data list using the selected indices
    for index in sorted(selected_indices, reverse=True):
        if 0 <= index < len(profiles_data):
            del profiles_data[index]
        else:
            print(f"Index {index} out of range. Skipping.")

    # Update the Treeview
    update_treeview()

    messagebox.showinfo('Delete Successful', 'Selected profiles deleted successfully!')

# Function to copy all profiles to clipboard
def copy_all():
    pyperclip.copy(str(profiles_data))
    messagebox.showinfo('Copy Successful', 'All profiles copied to clipboard!')

# Function to search for profiles
def search():
    search_text = search_entry.get().strip()
    if not search_text:
        messagebox.showwarning('No Search Text', 'Please enter a search keyword.')
        return

    search_results = []
    first_match = None

    # Clear existing highlights
    for item in tree.get_children():
        current_tags = tree.item(item, 'tags')
        if 'highlight' in current_tags:
            new_tags = tuple(tag for tag in current_tags if tag != 'highlight')
            tree.item(item, tags=new_tags)

    for profile in profiles_data:
        if re.search(search_text, profile['Name'], re.IGNORECASE) or re.search(search_text, profile['Job Title'], re.IGNORECASE):
            search_results.append(profile)

    if search_results:
        for item in tree.get_children():
            item_values = tree.item(item, 'values')
            item_tags = list(tree.item(item, 'tags'))  # Get current tags
            for profile in search_results:
                profile_values = (
                    profile['Name'], 
                    profile['Job Title'], 
                    profile['Profile Link'], 
                    profile['Email'] + " ✔" if profile['Email'] else 'Email not found',  # Adjusting for visual indicator
                    profile['Phone Number'] if profile['Phone Number'] else 'Phone number not found'
                )
                if profile_values == item_values:
                    tree.item(item, tags=('highlight',))
                    if first_match is None:
                        first_match = item
                    break
        # Auto-scroll to the first match
        if first_match:
            tree.see(first_match)
    else:
        messagebox.showinfo('No Results', 'No profiles found matching the search keyword.')

# Function to sort the Treeview column
def sort_column(col):
    global profiles_data
    profiles_data.sort(key=lambda x: x[col], reverse=sort_orders[col])
    sort_orders[col] = not sort_orders[col]
    update_treeview()

# Function to go back to main menu
def back():
    root.destroy()
    subprocess.run(["python3", "1._main_and_3._market_pages.py"])
    
# Initialize customtkinter GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("Scraped Profiles")
# Style for Treeview
style = ttk.Style()
style.theme_use("clam")                                                                                        # set the theme to use for ttk
root.geometry("1200x800+400+150")                                                                              # Setting the fixed size and position of the window
root.focus_force()                                                                                             # Bring the window to the front and focus it

# Use the native OS window decorations
root.overrideredirect(False)


# Customize the Treeview
style.configure("Treeview",
                background="#2e2e2e",
                foreground="white",
                rowheight=25,
                fieldbackground="#2e2e2e")

style.map('Treeview', background=[('selected', '#5a5a5a')])

# Customize the Treeview headings
style.configure("Treeview.Heading",
                background="#1FA557",
                foreground="white",
                relief="flat")

style.map("Treeview.Heading",
          background=[('active', '#14702B')])

# Label and Entry for page number input
page_number_label = ctk.CTkLabel(root, text="Page Number:")
page_number_label.pack(pady=5)
page_number_entry = ctk.CTkEntry(root, placeholder_text="Input page number...")
page_number_entry.pack(pady=5)

# Search bar
search_frame = ctk.CTkFrame(root)
search_frame.pack(fill='x', pady=5)

search_entry = ctk.CTkEntry(search_frame)
search_entry.pack(side='left')

# Search button
search_button = ctk.CTkButton(search_frame, text="Search", command=search)
search_button.pack(side= 'left')

# Create Treeview to display scraped data using ttk
columns = ('Name', 'Job Title', 'Profile Link', 'Email', 'Phone Number')
tree = ttk.Treeview(root, columns=columns, show='headings', style="Treeview")
sort_orders = {col: False for col in columns}                                                                   # Dictionary to keep track of sort orders

for col in columns:
    tree.heading(col, text=col, command=lambda _col=col: sort_column(_col))
tree.pack(fill='both', expand=True, pady=5)

# Define a tag for highlighting search results
tree.tag_configure('highlight', background='darkblue')

# Container frame for the buttons
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10)

# Uniform button style
button_style = {"corner_radius": 10, "fg_color": "#1FA557", "hover_color": "#14702B", "text_color": "#ffffff"}

# Button to update and display scraped data
update_button = ctk.CTkButton(button_frame, text="Gimme the Juice", command=lambda: update_gui(page_number_entry.get()), **button_style)
update_button.pack(side="left", padx=5)

# Button to export selected data
export_selected_button = ctk.CTkButton(button_frame, text="Export Selected", command=export_selected, **button_style)
export_selected_button.pack(side="left", padx=5)

# Button to export all data
export_all_button = ctk.CTkButton(button_frame, text="Export All", command=export_all, **button_style)
export_all_button.pack(side="left", padx=5)

# Button to copy selected data
copy_selected_button = ctk.CTkButton(button_frame, text="Copy Selected", command=copy_selected, **button_style)
copy_selected_button.pack(side="left", padx=5)

# Button to copy all data
copy_all_button = ctk.CTkButton(button_frame, text="Copy All", command=copy_all, **button_style)
copy_all_button.pack(side="left", padx=5)

# Button to delete selected data
delete_selected_button = ctk.CTkButton(button_frame, text="Delete Selected", command=delete_selected, **button_style)
delete_selected_button.pack(side="left", padx=5)

# Button to go back to main menu
delete_selected_button = ctk.CTkButton(button_frame, text="Back to Main Menu", command=back, **button_style)
delete_selected_button.pack(side="left", padx=5)

# Run the GUI
root.mainloop()



