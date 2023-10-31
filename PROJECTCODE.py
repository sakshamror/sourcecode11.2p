# Import necessary libraries
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import tkinter as tk
from tkinter import Entry, Button, Label, Frame, StringVar, messagebox, Entry

# Create a class for the RFID Bill Management application
class RFIDBillApp:
    # Initialize the class
    def __init__(self, root):
        # Set up the root window
        self.root = root
        self.root.title("RFID Bill Management")
        self.root.configure(bg="#f0f0f0")  # Set background color

        # Create an instance of the RFID reader
        self.reader = SimpleMFRC522()

        # Initialize variables
        self.bill = {}
        self.uid_label = Label(root, text="Hold an RFID card near the reader to add items to the bill.", bg="#f0f0f0", font=("Helvetica", 14))
        self.uid_label.pack(pady=20)

        # Create buttons and labels for the GUI
        self.read_uid_button = Button(root, text="Read UID", command=self.read_uid, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.read_uid_button.pack(pady=10)

        self.item_frame = Frame(root, bg="#f0f0f0")
        self.item_frame.pack()

        # Item description label and entry
        self.item_description_label = Label(self.item_frame, text="Item Description:", bg="#f0f0f0", font=("Helvetica", 12))
        self.item_description_label.pack(side="left")

        self.item_description_var = StringVar()
        self.item_description_entry = Entry(self.item_frame, textvariable=self.item_description_var, font=("Helvetica", 12))
        self.item_description_entry.pack(side="left")

        # Item price label and entry
        self.item_price_label = Label(self.item_frame, text="Item Price ($):", bg="#f0f0f0", font=("Helvetica", 12))
        self.item_price_label.pack(side="left")

        self.item_price_var = StringVar()
        self.item_price_var.set("0.00")  # Set an initial value
        self.item_price_entry = Entry(self.item_frame, textvariable=self.item_price_var, font=("Helvetica", 12))
        self.item_price_entry.pack(side="left")

        # Total Bill label
        self.total_label = Label(root, text="Total Bill:", bg="#f0f0f0", font=("Helvetica", 16, "bold"))
        self.total_label.pack(pady=20)

        # Item listbox to display added items
        self.item_listbox = tk.Listbox(root, selectmode=tk.SINGLE, font=("Helvetica", 12), width=60, height=10)
        self.item_listbox.pack(pady=10)

        # Delete Item and Send Mail buttons
        self.delete_button = Button(root, text="Delete Item", command=self.delete_item, bg="#FF5722", fg="white", font=("Helvetica", 12))
        self.delete_button.pack(pady=10)

        self.send_mail_button = Button(root, text="Send Mail", command=self.send_mail, bg="#2196F3", fg="white", font=("Helvetica", 12))
        self.send_mail_button.pack(pady=10)

        # Email entry and label
        self.email_label = Label(root, text="Enter Recipient Email:", bg="#f0f0f0", font=("Helvetica", 12))
        self.email_label.pack()
        
        self.email_entry = Entry(root, font=("Helvetica", 12))
        self.email_entry.pack()

        # Initialize total cost and total bill label
        self.total_cost = 0
        self.total_bill_label = Label(root, text="Total Bill: $0.00", bg="#f0f0f0", font=("Helvetica", 16, "bold"))
        self.total_bill_label.pack()

        # Define products and their prices using card UIDs as keys
        self.products = {
            772332845062: {'description': "Chips", 'price': 20},
            772672460190: {'description': "Chocolate", 'price': 10},
            146729224700: {'description': "Kurkure", 'price': 30},
            # Add more products with their UIDs here
        }

    # Method to read the UID from the RFID card
    def read_uid(self):
        id, _ = self.reader.read()

        if id == 0:
            return

        self.current_uid = id
        product_info = self.products.get(self.current_uid)

        if product_info:
            self.item_description_var.set(product_info['description'])
            self.item_price_var.set(product_info['price'])
            self.add_item()
        else:
            self.item_description_var.set("")
            self.item_price_var.set("0.00")
            print("Product information not found for this card.")

        self.uid_label.config(text=f"Card UID: {self.current_uid}")

    # Method to add an item to the bill
    def add_item(self):
        if hasattr(self, 'current_uid'):
            item_description = self.item_description_var.get()
            item_price = float(self.item_price_var.get())

            if self.current_uid in self.bill:
                self.bill[self.current_uid]['quantity'] += 1
            else:
                self.bill[self.current_uid] = {'description': item_description, 'price': item_price, 'quantity': 1}

            self.total_cost += item_price
            self.total_label.config(text=f"Total Bill: ${self.total_cost:.2f}")
            self.update_item_listbox()

            # Update the total bill label
            self.total_bill_label.config(text=f"Total Bill: ${self.total_cost:.2f}")
        else:
            print("Please read an RFID card first.")

    # Method to update the item listbox with added items
    def update_item_listbox(self):
        self.item_listbox.delete(0, tk.END)
        for uid, item in self.bill.items():
            description = item['description']
            price = item['price']
            quantity = item['quantity']
            self.item_listbox.insert(tk.END, f"Item: {description}, Price: ${price:.2f}, Quantity: {quantity}")

    # Method to delete an item from the bill
    def delete_item(self):
        selected_index = self.item_listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            uid_to_delete = list(self.bill.keys())[selected_index]
            deleted_item = self.bill.pop(uid_to_delete)
            deleted_item_price = deleted_item['price']
            deleted_item_quantity = deleted_item['quantity']
            self.total_cost -= (deleted_item_price * deleted_item_quantity)
            self.total_label.config(text=f"Total Bill: ${self.total_cost:.2f}")
            self.update_item_listbox()
            self.total_bill_label.config(text=f"Total Bill: ${self.total_cost:.2f}")
        else:
            messagebox.showinfo("Info", "Select an item to delete.")

    # Method to send an email (not implemented in this code)
    def send_mail(self):
        recipient_email = self.email_entry.get()
        if not recipient_email:
            messagebox.showinfo("Info", "Please enter a recipient's email address.")
            return

# Check if the script is run as the main program
if __name__ == "__main__":
    # Create the main Tkinter window and the RFIDBillApp instance
    root = tk.Tk()
    app = RFIDBillApp(root)
    root.geometry("800x600")  # Set the initial window size
    root.mainloop()
