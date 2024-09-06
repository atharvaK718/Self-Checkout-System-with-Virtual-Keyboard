import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import time

# Keyboard layout
keyboard_keys = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["0", "Delete", "Enter"]
]

# Key dimensions and layout settings
key_width = 100
key_height = 80
x_gap = 30
y_gap = 22
padding = 15

# Initialize MediaPipe for hand detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.9, min_tracking_confidence=0.9)

# Draw keyboard on the frame
def draw_keyboard(frame):
    global x_start, y_start
    frame_height, frame_width, _ = frame.shape
    rows = len(keyboard_keys)
    cols = max(len(row) for row in keyboard_keys)
    total_width = cols * key_width + (cols - 1) * x_gap + 2 * padding
    total_height = rows * key_height + (rows - 1) * y_gap + 2 * padding
    x_start = (frame_width - total_width) // 2
    y_start = (frame_height - total_height) // 2
    overlay = frame.copy()
    y = y_start + padding
    for row in keyboard_keys:
        x = x_start + padding
        for key in row:
            color = (200, 200, 200) if key not in ["Delete", "Enter"] else (150, 150, 150)
            cv2.rectangle(overlay, (x, y), (x + key_width, y + key_height), color, -1)
            cv2.putText(overlay, key, (x + key_width // 4, y + key_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            x += key_width + x_gap
        y += key_height + y_gap
    alpha = 0.5
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

# Get key based on hand coordinates
def get_key_from_coords(x, y, frame):
    global x_start, y_start
    frame_height, frame_width, _ = frame.shape
    rows = len(keyboard_keys)
    cols = max(len(row) for row in keyboard_keys)
    total_width = cols * key_width + (cols - 1) * x_gap + 2 * padding
    total_height = rows * key_height + (rows - 1) * y_gap + 2 * padding
    x_start = (frame_width - total_width) // 2
    y_start = (frame_height - total_height) // 2
    row = (y - y_start - padding) // (key_height + y_gap)
    col = (x - x_start - padding) // (key_width + x_gap)
    if 0 <= row < len(keyboard_keys) and 0 <= col < len(keyboard_keys[row]):
        return row, col
    return None, None

# Update text box with detected key
def update_text_box(text):
    global final_text
    if text == "Delete":
        final_text = final_text[:-1]
    elif text == "Enter":
        with open("input.txt", "w") as f:
            f.write(final_text)
        final_text = ""
    else:
        final_text += text
    text_box.delete(0, tk.END)
    text_box.insert(tk.END, final_text)

# Main application window
root = tk.Tk()
root.title("Virtual Keyboard")
text_box = ttk.Entry(root, font=('Helvetica', 24))
text_box.pack(pady=10, padx=10, fill=tk.X)
webcam_label = tk.Label(root)
webcam_label.pack()

# Capture video
cap = cv2.VideoCapture(0)
final_text = ""
last_key = None
last_press_time = time.time()

# Update video frame
def update_frame():
    global final_text, last_key, last_press_time, x_start, y_start
    ret, frame = cap.read()
    if not ret:
        root.after(10, update_frame)
        return
    draw_keyboard(frame)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame.shape[1])
            y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame.shape[0])
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            row, col = get_key_from_coords(x, y, frame)
            if row is not None and col is not None:
                key = keyboard_keys[row][col]
                cx = x_start + (col * (key_width + x_gap) + key_width // 2) + padding
                cy = y_start + (row * (key_height + y_gap) + key_height // 2) + padding
                l = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if l <= 50 and (time.time() - last_press_time) > 0.2:
                    if key != last_key:
                        last_key = key
                        update_text_box(key)
                        print(f"Detected Key: {key}")
                        last_press_time = time.time()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    imgtk = ImageTk.PhotoImage(image=img)
    webcam_label.imgtk = imgtk
    webcam_label.configure(image=imgtk)
    root.after(10, update_frame)

# Start updating frames
root.after(10, update_frame)

# Exit mechanism
def on_closing():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
