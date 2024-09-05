## Self-Checkout System with Virtual Keyboard

### Project Description

This project implements a Self-Checkout System that integrates computer vision and machine learning to enable a seamless checkout experience. The system uses a camera to scan products and a virtual keyboard for payment processing. Key technologies used in this project include:

- **OpenCV**: For real-time image processing and product detection.
- **Convolutional Neural Networks (CNN)**: To classify and recognize products based on their images.
- **Keras**: A high-level neural networks API used for building and training the CNN model.
- **Tkinter**: For creating the graphical user interface (GUI) of the virtual keyboard.
- **MediaPipe**: For hand tracking to facilitate the virtual keyboard interaction.

### Features

- **Product Scanning**: Uses OpenCV and CNN to scan and identify products from camera input.
- **Virtual Keyboard**: Implements a virtual keyboard using Tkinter for user input during the payment process.
- **Hand Tracking**: Employs MediaPipe for detecting and tracking hand movements to improve interaction with the virtual keyboard.

### Applications

- **Retail Stores**: Automate the checkout process to reduce lines and enhance customer experience. The system can be integrated into self-checkout kiosks to enable customers to scan and pay for their items independently.
- **Supermarkets**: Streamline the checkout process and reduce the need for cashier staff. The system can handle various product categories and process payments efficiently.
- **Libraries**: Facilitate the self-checkout of books and other items, improving the efficiency of checkouts and returns.
- **Events and Exhibitions**: Provide a fast and easy way for attendees to purchase merchandise or tickets without long wait times.
- **E-Commerce**: Enhance online shopping experiences with virtual checkout solutions and integrated payment processing.

### Installation

To set up the Self-Checkout System, follow these steps:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/self-checkout-system.git
    ```

2. **Navigate to the Project Directory**:
    ```bash
    cd self-checkout-system
    ```

3. **Install Dependencies**:
    Ensure you have Python 3.6 or higher installed. Create and activate a virtual environment, then install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

1. **Run the Product Scanning Module**:
    ```bash
    python product_scanner.py
    ```
    This will open a camera window where you can scan products.

2. **Run the Virtual Keyboard Module**:
    ```bash
    python virtual_keyboard.py
    ```
    This will open the virtual keyboard GUI for payment processing.

### Requirements

- Python 3.6+
- OpenCV
- Keras
- TensorFlow
- Tkinter (usually comes with Python)
- MediaPipe

You can install the required Python packages using:
```bash
pip install opencv-python keras tensorflow mediapipe
```

### Configuration

- **Model Training**: If you need to train your CNN model, use the `train_model.py` script provided. Make sure to place your dataset in the `data/` directory and adjust the paths in the script as needed.
- **Camera Settings**: Adjust the camera settings in `camera_config.py` if necessary to match your hardware.
