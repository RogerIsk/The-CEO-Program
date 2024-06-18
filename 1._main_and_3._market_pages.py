from tkinter import messagebox                                                      # Allows us to show pop-up messages
from PIL import Image, ImageTk                                                      # Allows us to work with images
from bs4 import BeautifulSoup                                                       # Allows us to scrape data from websites
import customtkinter as ctk                                                         # Allows us to customise the tkinter widgets more
import ttkbootstrap as ttk                                                          # Allows us to customise the tkinter widgets more
import subprocess                                                                   # Allows us to open other python files
import pandas as pd                                                                 # Allows us to work with the data in tables
import requests                                                                     # Allows us to send HTTP requests (like opening a website)
import json                                                                         # Allows us to work with JSON files
import os                                                                           # Allows us to work with the operating system (like creating folders)

# MARKET CODE =============================================================================================================

market_transaction_frame = None                                                     # Define the "market_transaction_frame" variable
current_table = ""                                                                  # Track the current active table
current_webscraping_function = None                                                 # Track the current webscraping function/ table

def display_web_tables(soup, table_class, function_name):                           # Complicated function to scrape and save tables from the web
    global current_table                                                            #   accessing the global variable 'current_table' so we know which table we are currently working with
    current_table = function_name                                                   #   the current table = 'indices' or 'trending_stocks' or etc.
    tables = soup.find_all('table', class_=table_class)                             #   find all tables with the 'table' tag and the specified class
    if tables:                                                                      #   if at least one table is found we continue with the code
        if not os.path.exists('market files'):                                      #       if the folder 'market' doesn't exist
            os.makedirs('market files')                                             #           create the folder 'market'
        combined_tb = pd.DataFrame()                                                #       creating a DataFrame on the go to hold all tables
        for i, table in enumerate(tables):                                          #       loop through each found table (example: government bonds has 73 tabes on the same page so the loop works 73 times)
            headers = [header.text.strip() for header in table.find_all('th')]      #           extract all headers from currently accessed table
            rows = []                                                               #           create an empty list to store rows
            for row in table.find_all('tr')[1:]:                                    #           loop through each row (excluding the header row)
                columns = row.find_all('td')                                        #               extract all columns from each row
                rows.append([col.text.strip() for col in columns])                  #               insert the cleaned text to rows list (which later goes in the DataFrame)
            tb = pd.DataFrame(rows, columns=headers)                                #           create DataFrame from headers and rows
            tb.index = tb.index + 1                                                 #           make it so the list index starts from 1 not 0 as usual 
            file_name = f'{function_name}_{i+1}.csv'                                #           make it so the saved file has a specific name
            file_path = os.path.join('market files', file_name)                     #           save the CSV file in the 'market files' folder
            tb.to_csv(file_path, index=False, mode='w')                             #           save the scraped table as a CSV file in the 'market files' folder with a specific name
            print(tb)                                                               #           prints the table
            combined_tb = pd.concat([combined_tb, tb], ignore_index=True)           #           add the table to the list of all tables for the current page
        update_treeview(tree, combined_tb.columns.tolist(), combined_tb.values.tolist())#   update the Treeview with the combined tables list (all tables from the current page)
    else:                                                                           #   if no tables are found
        print("No table found with the specified class.")                           #       print a message to the terminal

def get_indices():                                                                  # Function to scrape the indices table from the web
    url = 'https://www.investing.com/indices/major-indices'                         #   we get the URL of the website under the variable 'url'
    page = requests.get(url)                                                        #   this simulates opening the website in a browser
    soup = BeautifulSoup(page.text, 'html.parser')                                  #   this lets us take the HTML code of the website and use it as a string
    display_web_tables(soup, 'datatable-v2_table__93S4Y', 'indices')                #   this looks for the specific html code and table name that contain the table we want to scrape

def get_trending():                                                                 # Function to scrape the trending stocks table from the web
    url = 'https://www.investing.com/equities/trending-stocks'                      #   we get the URL of the website under the variable 'url'
    page = requests.get(url)                                                        #   this simulates opening the website in a browser
    soup = BeautifulSoup(page.text, 'html.parser')                                  #   this lets us take the HTML code of the website and use it as a string
    display_web_tables(soup, 'datatable-v2_table__93S4Y', 'trending_stocks')        #   this looks for the specific html code and table name that contain the table we want to scrape

def get_commodity_futures():                                                        # Function to scrape the commodity futures table from the web
    url = 'https://www.investing.com/commodities/real-time-futures'                 #   we get the URL of the website under the variable 'url'
    page = requests.get(url)                                                        #   this simulates opening the website in a browser
    soup = BeautifulSoup(page.text, 'html.parser')                                  #   this lets us take the HTML code of the website and use it as a string 
    display_web_tables(soup, 'datatable-v2_table__93S4Y', 'commodity_futures')      #   this looks for the specific html code and table name that contain the table we want to scrape             
      
def get_exchange_rates():                                                           # Function to scrape the exchange rates table from the web
    url = 'https://www.investing.com/currencies/streaming-forex-rates-majors'       #   we get the URL of the website under the variable 'url'
    page = requests.get(url)                                                        #   this simulates opening the website in a browser         
    soup = BeautifulSoup(page.text, 'html.parser')                                  #   this lets us take the HTML code of the website and use it as a string        
    display_web_tables(soup, 'datatable-v2_table__93S4Y', 'exchange_rates')         #   this looks for the specific html code and table name that contain the table we want to scrape                

def get_etfs():                                                                     # Function to scrape the ETFs table from the web
    url = 'https://www.investing.com/etfs/major-etfs'                               #   we get the URL of the website under the variable 'url'
    page = requests.get(url)                                                        #   this simulates opening the website in a browser          
    soup = BeautifulSoup(page.text, 'html.parser')                                  #   this lets us take the HTML code of the website and use it as a string                
    display_web_tables(soup, 'genTbl closedTbl crossRatesTbl elpTbl elp40', 'etfs') #   this looks for the specific html code and table name that contain the table we want to scrape                               

def get_government_bonds():                                                         # Function to scrape the government bonds table from the web
    url = 'https://www.investing.com/rates-bonds/world-government-bonds'            #   we get the URL of the website under the variable 'url'
    page = requests.get(url)                                                        #   this simulates opening the website in a browser                 
    soup = BeautifulSoup(page.text, 'html.parser')                                  #   this lets us take the HTML code of the website and use it as a string             
    display_web_tables(soup, 'genTbl closedTbl crossRatesTbl', 'government_bonds')  #   this looks for the specific html code and table name that contain the table we want to scrape                     

def get_funds():                                                                    # Function to scrape the funds table from the web
    url = 'https://www.investing.com/funds/major-funds'                             #   we get the URL of the website under the variable 'url'
    page = requests.get(url)                                                        #   this simulates opening the website in a browser                  
    soup = BeautifulSoup(page.text, 'html.parser')                                  #   this lets us take the HTML code of the website and use it as a string            
    display_web_tables(soup, 'genTbl closedTbl crossRatesTbl elpTbl elp40', 'funds')#   this looks for the specific html code and table name that contain the table we want to scrape                          

def get_cryptocurrencies():                                                         # Function to scrape the cryptocurrencies table from the web
    url = 'https://markets.businessinsider.com/cryptocurrencies'                    #   we get the URL of the website under the variable 'url'
    page = requests.get(url)                                                        #   this simulates opening the website in a browser                               
    soup = BeautifulSoup(page.text, 'html.parser')                                  #   this lets us take the HTML code of the website and use it as a string                                     
    display_web_tables(soup, 'table table--col-1-font-color-black table--suppresses-line-breaks table--fixed', 'cryptocurrencies')# this looks for the specific html code and table name that contain the table we want to scrape

def load_stock_data(table_name):                                                    # Function that loads the amount of owned stocks from JSON file corresponding to the currently scraped table (a number)
    market_files_dir = 'market files'                                               #   assigning the folder name to a variable so we can use it
    stock_data_file = os.path.join(market_files_dir, f'{table_name}_stocks.json')   #   telling the program where to find the file and it's name + assigning it to a variable so we can use that information
    if os.path.exists(stock_data_file):                                             #   if the file exists (in that folder & under that name)
        with open(stock_data_file, 'r') as file:                                    #       we get permission to read/extract data from the file before we open it
            return json.load(file)                                                  #           and we load the file so it can we can actually extract its data
    return {}                                                                       #   if the file doesn't exist the column with the 'owned stocks' amount will be empty when the table is shown

def save_new_stock_data(table_name, stock_data):                                    # Function to save the bought stocks data to a JSON file
    market_files_dir = 'market files'                                               #   giving the folder name a variable for later use
    if not os.path.exists(market_files_dir):                                        #   if the folder doesn't exist
        os.makedirs(market_files_dir)                                               #       create the folder
    stock_data_file = os.path.join(market_files_dir, f'{table_name}_stocks.json')   #   telling the code where to save the file and under what name
    with open(stock_data_file, 'w') as file:                                        #   open the file in write mode
        json.dump(stock_data, file)                                                 #       write the stock data to the file

def update_treeview(tree, headers, rows):                                           # Function to update the Treeview with the scraped data
    tree.delete(*tree.get_children())                                               #   this deletes all the table info from the Treeview widget
    stock_data = load_stock_data(current_table)                                     #   load the stock data from the JSON file
    tree["columns"] = ["Index", "Stock Count"] + headers                            #   add "Index" and "Stock Count" as the first columns
    tree.heading("Index", text="#")                                                 #   set the text of the "Index" column to "#" to indicate the index
    tree.heading("Stock Count", text="Owned")                                       #   set the text of the "Stock Count" column to "Owned" to indicate owned stocks
    tree.column("Index", anchor='w', width=25, stretch=False)                       #   set the width of the "Index" column and disable stretching so it doesnt change to a smaller size
    tree.column("Stock Count", anchor='center', width=60, stretch=False)            #   set the width of the "Stock Count" column and disable stretching so it doesnt change to a smaller size
    for header in headers:                                                          #   loop - for each header in the table
        tree.heading(header, text=header)                                           #       set the text of the header to the header name
        tree.column(header, anchor='center', width=80, minwidth=50)                 #       set the width of the header column and allow stretching
    for i, row in enumerate(rows, start=1):                                         #   loop - for each row in the table
        stock_count = stock_data.get(str(i), 0)                                     #       get stock count for the current stock which is loaded from the JSON file
        tree.insert("", "end", values=[i, stock_count] + row)                       #       insert the row into the Treeview widget with the new stock count

def update_stock_count_in_treeview(tree):                                           # Function to update the stock count in the Treeview after webscraping/buying/selling
    stock_data = load_stock_data(current_table)                                     #   load the amount of owned stocks data from the JSON file
    for item in tree.get_children():                                                #   loop - for each item in the Treeview widget
        stock_index = tree.item(item, 'values')[0]                                  #       get the stocks index (the stock number in the list of stocks)
        stock_count = stock_data.get(str(stock_index), 0)                           #       get the amount of owned stocks for that specific stock number on the list
        current_values = tree.item(item, 'values')                                  #       get how many stock
        new_values = [current_values[0], stock_count] + current_values[2:]          #       create a new list with the updated stock count
        tree.item(item, values=new_values)                                          #       update the Treeview widget with the new stock count

def clear_treeview(tree):                                                           # Function to clear the Treeview widget
    tree.delete(*tree.get_children())                                               #   delete all the rows in the Treeview widget
    tree["columns"] = []                                                            #   clear the text from the columns
    tree.heading("#0", text="")                                                     #   clear the text from the headings/first column

def show_treeview():                                                                # Function to show the Treeview widget
    treeview_frame.pack(padx=(330, 0), pady=0, fill='both', expand=True)            #   show the Treeview frame

def show_market_buttons():                                                          # Function to show the buttons in the market page   
    show_treeview()                                                                 #   show the Treeview widget where the tables will appear
    
    def buy_stocks():                                                               #   Function to buy stocks (add an amount of stocks to the owned stocks in the JSON file)
        try:                                                                        #       try to do the following
            amount = int(search_bar.get())                                          #           get the amount of stocks to buy from the search bar
            selected_items = tree.selection()                                       #           get the selected items from the Treeview widget
            if selected_items:                                                      #           if there are selected items
                stock_data = load_stock_data(current_table)                         #               load the stock data from the JSON file
                for item in selected_items:                                         #               loop - for each selected item
                    stock_index = tree.item(item, 'values')[0]                      #                   get the stock index from the JSON file
                    if str(stock_index) not in stock_data:                          #                   if the stock index is not in the JSON file
                        stock_data[str(stock_index)] = 0                            #                       set the stock count to 0
                    stock_data[str(stock_index)] += amount                          #                   add the amount of 'bought' stocks to the current stock amount
                save_new_stock_data(current_table, stock_data)                      #               save the new stock data to the JSON file
                messagebox.showinfo("Transaction Successful", f"Bought {amount} of each selected stock")# confirmation message
                current_webscraping_function()                                      #               Re-scrape the current table to update the owned stock count 
            else:                                                                   #           if there are no selected items
                messagebox.showwarning("No Selection", "Please select a stock to buy.") #           warning message
        except ValueError:                                                          #       if the input is not a number
            messagebox.showerror("Invalid Input", "Please enter a valid number.")   #           error message

    def sell_stocks():                                                              #   Function to sell stocks (remove an amount of stocks from the owned stocks from the JSON file)
        try:                                                                        #       try to do the following
            amount = int(search_bar.get())                                          #           get the amount of stocks to sell from the search bar
            selected_items = tree.selection()                                       #           get the selected items from the Treeview widget
            if selected_items:                                                      #           if there are selected items
                stock_data = load_stock_data(current_table)                         #               load the stock data from the JSON file
                for item in selected_items:                                         #               loop - for each selected item
                    stock_index = tree.item(item, 'values')[0]                      #                   get the stock index from the JSON file
                    if str(stock_index) in stock_data:                              #                   if the stock index is in the JSON file
                        if stock_data[str(stock_index)] >= amount:                  #                       if the amount of stocks is greater or equal to the amount to sell
                            stock_data[str(stock_index)] -= amount                  #                           subtract the amount of 'sold' stocks from the current stock amount
                            if stock_data[str(stock_index)] == 0:                   #                           if the stock amount is 0
                                del stock_data[str(stock_index)]                    #                               delete the stock from the JSON file
                            messagebox.showinfo("Transaction Successful", f"Sold {amount} of {stock_index}") #  confirmation message
                        else:                                                       #                       if the amount of stocks is less than the amount to sell
                            messagebox.showwarning("Not Enough Stocks", f"Not enough stocks to sell {amount} of {stock_index}.") # warning message
                    else:                                                           #                   if the stock index is not in the JSON file
                        messagebox.showwarning("No Stocks", f"No stocks available to sell for {stock_index}.") # warning message
                save_new_stock_data(current_table, stock_data)                      #               save the new stock data to the JSON file
                current_webscraping_function()                                      #           Re-scrape the current table to update the owned stock count
            else:                                                                   #           if there are no selected items
                messagebox.showwarning("No Selection", "Please select a stock to sell.")#           warning message
        except ValueError:                                                          #       if the input is not a number
            messagebox.showerror("Invalid Input", "Please enter a valid number.")   #           error message

    def show_selected_stock_info():                                                 #   Function to show the total amount of selected stocks
        selected_items = tree.selection()                                           #       get the selected items from the Treeview widget
        stock_data = load_stock_data(current_table)                                 #       load the stock data from the JSON file
        total_stocks = 0                                                            #       set the total amount of selected stocks to 0 (default)
        for item in selected_items:                                                 #       loop - for each selected item
            stock_index = tree.item(item, 'values')[0]                              #           get the stock index from the JSON file
            total_stocks += stock_data.get(str(stock_index), 0)                     #           add the amount of selected stocks to the total amount of selected stocks
        messagebox.showinfo("Stock Information", f"Total stocks selected: {total_stocks}")# show the total amount of selected stocks

    global market_transaction_frame                                                 #   accessing the global variable 'market_transaction_frame' so we can use it
    if market_transaction_frame is not None:                                        #   if the old transaction frame is visible (not None)
        market_transaction_frame.place_forget()                                     #       forget (hide) the transaction frame

    market_transaction_frame = ttk.Frame(root)                                      #   create a new frame for the transaction buttons
    market_transaction_frame.place(relx=0, rely=0.461)                              #   place the frame in the window

    search_bar = ttk.Entry(market_transaction_frame, width=20, font=('Helvetica', 15))# create a search bar for the amount of stocks to buy/sell
    search_bar.pack(side='bottom', padx=(20, 0), fill='x')                          #   place the search bar in the frame
    search_bar.insert(0, "Enter number")                                            #   set the default text in the search bar

    buy_button = ctk.CTkButton(market_transaction_frame, text="BUY", font=('Helvetica', 40, 'bold'), width=140, height=110, fg_color='#137501', hover_color='#39c146', command=buy_stocks)
    buy_button.pack(side='left', padx=(20, 5), pady=(0, 10)) # create a buy button, place it in the frame and customise it

    sell_button = ctk.CTkButton(market_transaction_frame, text="Sell", font=('Helvetica', 30, 'bold'), width=140, height=50, fg_color="#750e01", hover_color='#e05c5c', command=sell_stocks)
    sell_button.pack(padx=(5, 0), pady=(0, 10)) # create a sell button, place it in the frame and customise it

    info_button = ctk.CTkButton(market_transaction_frame, text="Info", font=('Helvetica', 30, 'bold'), width=140, height=50, fg_color="#007bff", hover_color='#0056b3', command=show_selected_stock_info)
    info_button.pack(padx=(5, 0), pady=(0, 10)) # create an info button, place it in the frame and customise it

    market_buttons = [                                                              #   create a list of tuples with the name of the button and the function it calls
        ("Indices", get_indices),                                                   #       the name of the button and the function that scrapes the table
        ("Trending Stocks", get_trending),                                          #
        ("Commodity Futures", get_commodity_futures),                               #
        ("Exchange Rates", get_exchange_rates),                                     #
        ("ETFs", get_etfs),                                                         #
        ("Government Bonds", get_government_bonds),                                 #
        ("Funds", get_funds),                                                       #
        ("Cryptocurrencies", get_cryptocurrencies)]                                 #

    for widget in button_frame.winfo_children():                                    #   loop - for each widget in the button frame
        widget.destroy()                                                            #       destroy the previous refresh and back buttons before creating new ones

    for text, command in market_buttons:                                            #   loop - for each button in the list of buttons do those thing
        button = ctk.CTkButton(button_frame, text=text, width=290, height=25, anchor='right', font=('Helvetica', 18, 'bold'))
        button.pack(padx=20, ipady=(5), pady=(10, 0))
        button.configure(command=lambda cmd=command: [show_treeview(), cmd(), set_current_webscraping_function(cmd)])

    # Create a refresh button to get the market page to its original form
    refresh_button = ctk.CTkButton(button_frame, text="Clear Screen", width=290, height=100, anchor='right', font=('Helvetica', 40, 'bold'), fg_color='#294f73', hover_color='#1d8ab5')
    refresh_button.pack(padx=20, pady=(210, 10))
    refresh_button.configure(command=lambda: clear_treeview(tree))
    refresh_button.configure(command=lambda: [clear_treeview(tree), search_bar.delete(0, 'end')])
    refresh_button.configure(command=lambda: [clear_treeview(tree), search_bar.delete(0, 'end'), search_bar.insert(0, "Enter number")])

    # Create a back button to return to the main page
    back_button = ctk.CTkButton(button_frame, text="Main Menu", width=290, height=100, anchor='right', font=('Helvetica', 45, 'bold'), fg_color='#294f73', hover_color='#1d8ab5')
    back_button.pack(padx=20, pady=(0, 20))
    back_button.configure(command=lambda: call_main_page_buttons())

def set_current_webscraping_function(function):                                     # Function to set the currently active webscraped table
    global current_webscraping_function                                             #  accessing the global variable 'current_webscraping_function' so we can use it
    current_webscraping_function = function                                         #  funcion is set to the currently active webscraped table

# MAIN PAGE CODE ==========================================================================================================

def open_employee_page():                                                           # Function to open the employee page
    root.destroy()                                                                  # Close the main window
    subprocess.run(["python3", "2._employees.py"])                                  # Open the employee page

def open_music_player():                                                            # Function to open the music player window
    root.destroy()                                                                  # Close the main window
    subprocess.run(["python3" , "../bravobravo/4._music_player.py"])                # Open the music player window

def call_main_page_buttons():                                                       # Function to return from the market page to the main page
    treeview_frame.pack_forget()                                                    #   hide the Treeview frame 
    for widget in button_frame.winfo_children():                                    #   loop - for each widget in the button frame
        widget.destroy()                                                            #       destroy the previous buttons before creating new ones
    if market_transaction_frame is not None:                                        #   if the old transaction frame is visible (not None) 
        market_transaction_frame.place_forget()                                     #       forget (hide) the transaction frame

    # Create the main menu buttons and customise them to do what they are supposed to do and look like they are supposed to look
    main_buttons = ["Employees", "Market", "Music", "Exit"]
    for text in main_buttons:
        if text == "Employees":
            button = ctk.CTkButton(button_frame, text=text, width=290, height=100, anchor='center', font=('Helvetica', 45, 'bold'), fg_color='#174487', hover_color='#5391f5', bg_color='#1d1e1f')
            button.configure(command=lambda: open_employee_page())
            button.pack(padx=20, pady=(20,0))
        elif text == "Market":
            button = ctk.CTkButton(button_frame, text=text, width=290, height=100, anchor='center', font=('Helvetica', 45, 'bold'), fg_color='#0f6961', hover_color='#19d1b9', bg_color='#1d1e1f')
            button.configure(command=lambda: show_market_buttons())
            button.pack(padx=20, pady=(20))
        elif text == "Music":
            button = ctk.CTkButton(button_frame,command=open_music_player, text=text, width=290, height=100, anchor='center', font=('Helvetica', 45, 'bold'), fg_color='#268717', hover_color='#59d119', bg_color='#1d1e1f')
            button.pack(padx=20, pady=(0,20))
        elif text == "Exit":
            button = ctk.CTkButton(button_frame, text=text, width=290, height=100, anchor='center', font=('Helvetica', 45, 'bold'), fg_color='#8f9110', hover_color='#d1d119', bg_color='#1d1e1f')
            button.configure(command=lambda: root.destroy())
            button.pack(padx=20, pady=(0, 320))

root = ttk.Window(themename='darkly')                                               # Create the main page window and give it a dark style to the window
root.wm_attributes('-alpha', 1)                                                     # Set the main page window opacity to 1 (fully visible) in case we wanna edit that later
root.title("The CEO Program")                                                       # Set the main page window title
root.geometry("1200x800+400+150")                                                   # Set the main page window size and position
root.resizable(False, False)                                                        # Disable window resizing

background_image = 'program files/main_page_background.jpg'                         # Set the background image of the main page
img = Image.open(background_image)                                                  # Open the background image
img = ImageTk.PhotoImage(img)                                                       # Convert the image to a format that can be used in tkinter
img_label = ttk.Label(root, image=img)                                              # Create a label for the image
img_label.place(x=0, y=0, relwidth=1, relheight=1)                                  # Place the image label in the window

button_frame = ttk.Frame(root)                                                      # Create a frame for the buttons
button_frame.place(relx=0, rely=0.5, anchor='w')                                    # Place the frame in the window

treeview_frame = ttk.Frame(root)                                                    # Create a frame for the Treeview widget in the market page
treeview_frame.pack(padx=(300, 7), pady=7, fill='both', expand=True)                # Place the frame in the window
tree = ttk.Treeview(treeview_frame, show='headings', style="Treeview")              # Create the Treeview widget
scrollbar = ttk.Scrollbar(treeview_frame, orient='vertical', command=tree.yview)    # Create a scrollbar for the Treeview widget
scrollbar.pack(side='right', fill='y')                                              # Place the scrollbar in the window
tree.config(yscrollcommand=scrollbar.set)                                           # Configure the Treeview widget with the scrollbar
tree.pack(side='left', fill='both', expand=True)                                    # Place the Treeview widget in the window

call_main_page_buttons()
root.mainloop()