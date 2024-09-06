import qrcode
import random
import string
import os

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

if __name__ == "__main__":
    # Example usage
    qr_file = generate_random_payment_qr_code()
    print(f"Random payment QR code generated: {qr_file}")
