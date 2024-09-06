import cv2
import numpy as np
import pandas as pd
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk,ImageDraw
import mediapipe as mp
import time
import qrcode
import random
import string
import os


# Constants
WINDOW_WIDTH = 675
WINDOW_HEIGHT = 675
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480
KEYBOARD_KEYS = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["0", "Delete", "Enter"]
]
KEY_WIDTH = 80
KEY_HEIGHT = 60
X_GAP = 20
Y_GAP = 15
PADDING = 10

# Load product data and model
product_data = pd.read_csv("ProductData.csv")
product_info = {
    row['Product_ID']: {
        'name': row['Product_Name'],
        'price': float(row['Price'].replace('$', '')),
        'discount': float(row['Discount'].replace("%", '')) / 100.0
    } for index, row in product_data.iterrows()
}
model = load_model("self_checkout_model.h5")

def generate_random_string(length=10):
    """Generate a random string of letters and digits."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_qr_code(data, file_name="payment_qr.png"):
    """Generate a QR code from the provided data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_name)
    print(f"QR code saved as {file_name}")

def generate_random_payment_qr_code(directory="qr_codes"):
    """Generate a random QR code for payment and save it to a file."""
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate random payment data
    random_payment_id = generate_random_string(12)  # e.g., a random transaction ID
    payment_data = f"payment_id:{random_payment_id};amount:100.00"  # Example payment info

    # Create file name based on the payment ID
    file_name = os.path.join(directory, f"{random_payment_id}.png")

    # Generate and save the QR code
    generate_qr_code(payment_data, file_name)
    return file_name

class SelfCheckoutSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Self-Checkout System")
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        self.current_product = None
        self.scanned_products = []
        self.total_price = 0
        self.cap = cv2.VideoCapture(0)
        self.final_text = ""
        self.last_key = None
        self.last_press_time = time.time()
        
        self.setup_ui()
        self.update_frame()
    
    def setup_ui(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 12, 'bold'), padding=10)
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TEntry', font=('Helvetica', 12))
        
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        self.webcam_label = ttk.Label(self.main_frame)
        self.webcam_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.info_frame = ttk.Frame(self.main_frame, padding="10")
        self.info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.product_label = ttk.Label(self.info_frame, text="Product: ")
        self.product_label.grid(row=0, column=0, sticky="w")
        
        self.price_label = ttk.Label(self.info_frame, text="Price: $0.00")
        self.price_label.grid(row=1, column=0, sticky="w")
        
        self.total_label = ttk.Label(self.info_frame, text="Total: $0.00")
        self.total_label.grid(row=2, column=0, sticky="w")
        
        self.scan_button = ttk.Button(self.main_frame, text="Scan Product", command=self.scan_product)
        self.scan_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        self.show_bill_button = ttk.Button(self.main_frame, text="Show Bill", command=self.show_bill)
        self.show_bill_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    
    def recognize_product(self, frame):
        img = cv2.resize(frame, (150, 150))
        img = img.astype("float") / 255.0
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        prediction = model.predict(img)
        confidence_threshold = 0.92
        product_class = np.argmax(prediction[0])
        confidence = prediction[0][product_class]
        if confidence < confidence_threshold:
            return None
        product_id = int(list(product_info.keys())[product_class])
        return product_info[product_id]
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.master.after(10, self.update_frame)
            return
        
        frame = cv2.resize(frame, (WEBCAM_WIDTH, WEBCAM_HEIGHT))
        product = self.recognize_product(frame)
        self.current_product = product
        
        if product:
            cv2.putText(frame, f"Product: {product['name']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Price: ${product['price']:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No product identified", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img)
        self.webcam_label.img_tk = img_tk
        self.webcam_label.config(image=img_tk)
        
        self.master.after(10, self.update_frame)
    
    def scan_product(self):
        if self.current_product:
            self.scanned_products.append(self.current_product)
            self.total_price += self.current_product['price'] * (1 - self.current_product['discount'])
            self.update_info_labels()
    
    def update_info_labels(self):
        self.product_label.config(text=f"Product: {len(self.scanned_products)} item(s)")
        self.price_label.config(text=f"Last Price: ${self.current_product['price']:.2f}")
        self.total_label.config(text=f"Total: ${self.total_price:.2f}")
    
    def show_bill(self):
        bill_window = tk.Toplevel(self.master)
        bill_window.title("Bill Summary")
        
        bill_frame = ttk.Frame(bill_window, padding="10")
        bill_frame.pack(expand=True, fill=tk.BOTH)
        
        columns = ('product', 'price', 'quantity', 'discount', 'discounted_price', 'total')
        tree = ttk.Treeview(bill_frame, columns=columns, show='headings')
        tree.heading('product', text='Product')
        tree.heading('price', text='Price')
        tree.heading('quantity', text='Quantity')
        tree.heading('discount', text='Discount')
        tree.heading('discounted_price', text='Discounted Price')
        tree.heading('total', text='Total')
        
        product_counts = {}
        for product in self.scanned_products:
            if product['name'] in product_counts:
                product_counts[product['name']] += 1
            else:
                product_counts[product['name']] = 1
        
        for product_name, quantity in product_counts.items():
            product = next(p for p in self.scanned_products if p['name'] == product_name)
            price = product['price']
            discount = product['discount']
            discounted_price = price * (1 - discount)
            total = quantity * discounted_price
            tree.insert('', 'end', values=(
                product_name,
                f"${price:.2f}",
                quantity,
                f"{discount*100:.0f}%",
                f"${discounted_price:.2f}",
                f"${total:.2f}"
            ))
        
        tree.pack(expand=True, fill=tk.BOTH)
        
        total_label = ttk.Label(bill_frame, text=f"Total Price: ${self.total_price:.2f}", font=('Helvetica', 14, 'bold'))
        total_label.pack(pady=10)
        
        proceed_button = ttk.Button(bill_frame, text="Proceed to Payment", command=lambda: [bill_window.destroy(), self.open_payment_window()])
        proceed_button.pack(pady=10)
        
        # Adjust window size to fit content
        bill_window.update()
        window_width = tree.winfo_width()   # Add some padding
        window_height = bill_frame.winfo_height()   # Add some padding
        bill_window.geometry(f"{window_width}x{window_height}")
    
    def open_payment_window(self):
        self.payment_window = tk.Toplevel(self.master)
        self.payment_window.title("Payment")
        self.payment_window.geometry("400x300")
        
        ttk.Label(self.payment_window, text=f"Total Price: ${self.total_price:.2f}", font=('Helvetica', 16)).pack(pady=10)
        ttk.Label(self.payment_window, text="Enter Amount:").pack(pady=5)
        
        self.amount_entry = ttk.Entry(self.payment_window, font=('Helvetica', 14))
        self.amount_entry.pack(pady=5)
        def open_virtual_keyboard():
            root.destroy()
            subprocess.run(['python','virtualkeyboard.py'])
        ttk.Button(self.payment_window, text="Use Virtual Keyboard", command=self.open_virtual_keyboard).pack(pady=10)
        ttk.Button(self.payment_window, text="Pay", command=self.process_payment).pack(pady=10)
    
    def process_payment(self):
        try:
            entered_amount = float(self.amount_entry.get())
            if entered_amount >= self.total_price:
                change = entered_amount - self.total_price
                self.payment_window.destroy()
                self.show_thank_you(change)
            else:
                messagebox.showwarning("Payment", "Insufficient balance. Please try again.")
        except ValueError:
            messagebox.showwarning("Payment", "Invalid amount entered. Please enter a valid number.")
    def open_payment_window(self):
        self.payment_window = tk.Toplevel(self.master)
        self.payment_window.title("Payment")
        self.payment_window.geometry("400x200")
        
        ttk.Label(self.payment_window, text=f"Total Price: ${self.total_price:.2f}", font=('Helvetica', 16)).pack(pady=20)
        
        ttk.Button(self.payment_window, text="Pay Cash", command=self.process_cash_payment).pack(pady=10)
        ttk.Button(self.payment_window, text="Pay with QR Code", command=self.show_qr_code).pack(pady=10)

    def show_qr_code(self):
        qr_window = tk.Toplevel(self.master)
        qr_window.title("QR Code Payment")
        qr_window.geometry("400x500")
        
        ttk.Label(qr_window, text="Scan QR Code to Pay", font=('Helvetica', 18, 'bold')).pack(pady=20)
        
        # Load the QR code image from the specified path
        qr_path = r"V:/VIT/Project/Self checkout machine virtual keyboard with opencv/SelfCheckoutMachine/qr_codes/ZDRlPMXIz63X.png"
        qr_image = Image.open(qr_path)
        qr_image = qr_image.resize((200, 200), Image.LANCZOS)
        qr_photo = ImageTk.PhotoImage(qr_image)
        
        # Display the QR code image
        qr_label = ttk.Label(qr_window, image=qr_photo)
        qr_label.image = qr_photo
        qr_label.pack(pady=10)
        
        ttk.Label(qr_window, text=f"Amount: ${self.total_price:.2f}", font=('Helvetica', 14)).pack(pady=10)
        ttk.Button(qr_window, text="Confirm Payment", command=lambda: self.show_thank_you(0, qr_window)).pack(pady=10)

    
    def show_thank_you(self, change):
        thank_you_window = tk.Toplevel(self.master)
        thank_you_window.title("Thank You!")
        thank_you_window.geometry("400x200")
        
        ttk.Label(thank_you_window, text="Thank you! Visit again!", font=('Helvetica', 18, 'bold')).pack(pady=20)
        ttk.Label(thank_you_window, text=f"Your change: ${change:.2f}", font=('Helvetica', 14)).pack(pady=10)
        ttk.Button(thank_you_window, text="Close", command=self.reset_checkout).pack(pady=10)
    
    
    def process_cash_payment(self):
        self.payment_window.destroy()
        self.show_thank_you(0)

    def show_thank_you(self, change, previous_window=None):
        if previous_window:
            previous_window.destroy()
        
        thank_you_window = tk.Toplevel(self.master)
        thank_you_window.title("Thank You!")
        thank_you_window.geometry("400x200")
        
        ttk.Label(thank_you_window, text="Thank you! Visit again!", font=('Helvetica', 18, 'bold')).pack(pady=20)
        if change > 0:
            ttk.Label(thank_you_window, text=f"Your change: ${change:.2f}", font=('Helvetica', 14)).pack(pady=10)
        ttk.Button(thank_you_window, text="Close", command=self.reset_checkout).pack(pady=10)

    
    def reset_checkout(self):
        self.scanned_products = []
        self.total_price = 0
        self.update_info_labels()
        self.master.focus_set()
    
    def open_virtual_keyboard(self):
        self.keyboard_window = tk.Toplevel(self.master)
        self.keyboard_window.title("Virtual Keyboard")
        self.keyboard_window.geometry("600x500")
        
        self.text_box = ttk.Entry(self.keyboard_window, font=('Helvetica', 18))
        self.text_box.pack(pady=10, padx=10, fill=tk.X)
        
        self.keyboard_canvas = tk.Canvas(self.keyboard_window, width=600, height=400)
        self.keyboard_canvas.pack(pady=10)
        
        self.draw_keyboard()
        self.keyboard_canvas.bind("<Button-1>", self.on_keyboard_click)
    
    def draw_keyboard(self):
        x_start = PADDING
        y_start = PADDING
        for row in KEYBOARD_KEYS:
            x = x_start
            for key in row:
                color = "#DDDDDD" if key not in ["Delete", "Enter"] else "#BBBBBB"
                self.keyboard_canvas.create_rectangle(x, y_start, x + KEY_WIDTH, y_start + KEY_HEIGHT, fill=color, outline="black")
                self.keyboard_canvas.create_text(x + KEY_WIDTH // 2, y_start + KEY_HEIGHT // 2, text=key, font=('Helvetica', 14, 'bold'))
                x += KEY_WIDTH + X_GAP
            y_start += KEY_HEIGHT + Y_GAP
    
    def on_keyboard_click(self, event):
        row = (event.y - PADDING) // (KEY_HEIGHT + Y_GAP)
        col = (event.x - PADDING) // (KEY_WIDTH + X_GAP)
        if 0 <= row < len(KEYBOARD_KEYS) and 0 <= col < len(KEYBOARD_KEYS[row]):
            key = KEYBOARD_KEYS[row][col]
            self.update_text_box(key)
    
    def update_text_box(self, text):
        if text == "Delete":
            self.final_text = self.final_text[:-1]
        elif text == "Enter":
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(tk.END, self.final_text)
            self.keyboard_window.destroy()
        else:
            self.final_text += text
        self.text_box.delete(0, tk.END)
        self.text_box.insert(tk.END, self.final_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SelfCheckoutSystem(root)
    root.mainloop()