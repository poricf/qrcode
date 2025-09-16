
url = "https://o-and-o-somaletera-type-o2-or-a2.vercel.app/"
filename = "o-and-o-somaletera-type-o2-or-a2.png"


import qrcode
from PIL import Image

def generate_qr(link: str, filename: str):
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # 1 = smallest size, increase for more data
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,  # pixel size of each box
        border=4,     # border width
    )
    qr.add_data(link)
    qr.make(fit=True)

    # Generate image with transparent background
    img = qr.make_image(fill_color="black", back_color="transparent")

    # Save as PNG with transparency
    img.save(filename)

# Example usage
generate_qr(url , filename)
