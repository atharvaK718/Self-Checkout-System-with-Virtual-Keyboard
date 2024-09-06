import cv2 
import numpy as np
import pandas as pd
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

training_data = [
    "V:/VIT/Project/Self checkout machine virtual keyboard with opencv/TrainingDataforSelfCheckoutMachine/TrainingData/1001",
    "V:/VIT/Project/Self checkout machine virtual keyboard with opencv/TrainingDataforSelfCheckoutMachine/TrainingData/1002",
    "V:/VIT/Project/Self checkout machine virtual keyboard with opencv/TrainingDataforSelfCheckoutMachine/TrainingData/1003" 
]

product_data_path = "V:/VIT/Project/Self checkout machine virtual keyboard with opencv/TrainingDataforSelfCheckoutMachine/ProductData.csv"
product_data = pd.read_csv(product_data_path)
product_info = {
    row['Product_ID']: {
      'name': row['Product_Name'],
      'price': float(row['Price'].replace('$','')),
      'discount': float(row['Discount'].replace("%",'')) / 100.0
    } for index, row in product_data.iterrows()
}
model = load_model("self_checkout_model.h5")
current_discounted_price = 0
total_price = 0
count_products = 0

cap = cv2.VideoCapture(0)
def recognize_product(frame, model):
    img = cv2.resize(frame, (150,150))
    img = img.astype("float") / 255.0
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    prediction = model.predict(img)
    confidence_threshold = 0.92
    product_class = np.argmax(prediction[0])
    confidence = prediction[0][product_class]
    if confidence < confidence_threshold:
      return "No product identified", None, None, None
    product_id = int(list(product_info.keys())[product_class])
    product = product_info[product_id]
    discounted_price = product['price'] * (1 - product['discount'])
    return product['name'], product['price'], product['discount'], discounted_price

def open_payment_window():
    def process_payment():
        try:
            entered_amount = float(amount_entry.get())
            if entered_amount >= total_price:
                change = entered_amount - total_price
                messagebox.showinfo("Payment", f"Thanks for making the purchase. Your change is ${change:.2f}.")
            else:
                messagebox.showwarning("Payment", " Balance is not enough, please try again.")
        except ValueError:
            messagebox.showwarning("Payment", "Invalid amount entered, please enter valid number")
    payment_window = tk.Toplevel(root)
    payment_window.title("Payment")
    tk.Label(payment_window, text=f"Total Price: ${total_price:.2f}").pack(pady=10)
    tk.Label(payment_window, text="Enter Amount:").pack(pady=5)
    amount_entry = tk.Entry(payment_window)
    amount_entry.pack(pady=5)
    tk.Button(payment_window, text="Pay", command=process_payment, font=('Helvetica',16)).pack(pady=20)

def update_frame():
    global current_discounted_price, total_price, count_products
    ret, frame = cap.read()
    if not ret:
        return
    try:
        product_name, product_price, discount, discounted_price = recognize_product(frame, model)
        current_discounted_price = discounted_price
        if product_name == "No product identified":
            text = product_name
        else:
            text = (
                f"Product: {product_name}\n"
                f"Price: {product_price:.2f}\n"
                f"Discount: {discount*100:.0f}%\n"
                f"Price After Discount: ${discounted_price:.2f}\n"
                f"Total Products: {count_products}\n"
                f"Total Price: ${total_price:.2f}"
            )

        y0, dy = 50, 30
        for i, line in enumerate(text.split('\n')):
            y = y0 + i * dy
            cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2, cv2.LINE_AA)
        
        frame = cv2.resize(frame, (640,480))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img)
        video_label.img_tk = img_tk
        video_label.config(image=img_tk)
    except Exception as e:
        print(f"Error during recognition: {e}")
    root.after(10, update_frame)

def scan_product():
    global current_discounted_price, total_price, count_products
    count_products += 1
    total_price += current_discounted_price

root = tk.Tk()
root.title("Self Checkout Machine")
root.geometry("800x600")
video_label = tk.Label(root)
video_label.pack()
scan_button = tk.Button(root, text="Scan Product", command=scan_product, font=('Helvetica',16,'bold'), width=20, height=2)
scan_button.pack(side=tk.LEFT, padx=20, pady=10)
pay_button = tk.Button(root, text="Payment", command=open_payment_window, font=('Helvetica',16,'bold'), width=20, height=2)
pay_button.pack(side=tk.RIGHT, padx=20, pady=10)

update_frame()

def on_closing():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()


    
    




    
    
    
    
