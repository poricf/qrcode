import qrcode
from PIL import Image

def generate_transparent_qr(url: str, filename: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR with white background first
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # Make white pixels transparent
    new_pixels = []
    for p in img.getdata():
        if p[0] > 200 and p[1] > 200 and p[2] > 200:  # near-white
            new_pixels.append((255, 255, 255, 0))
        else:
            new_pixels.append(p)
    img.putdata(new_pixels)

    img.save(filename)
    print(f"QR code saved as {filename}")

generate_transparent_qr(
    "https://seken-lycee-type-01.vercel.app/",
    "seken-lycee-type-01.png"
)
