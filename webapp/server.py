from flask import Flask, render_template, request, send_file
import io
import math
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps

app = Flask(__name__)


def _create_default_temer_logo(size):
    # Circular TEMER badge using brand c`olors
    # primary:  #7A9B2C  -> (122, 155, 44)
    # secondary: #B09048 -> (176, 144, 72)
    logo = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)

    # Outer circle - secondary gold
    draw.ellipse((0, 0, size - 1, size - 1), fill=(176, 144, 72, 255))

    # Slight inner shading for a subtle depth effect (lighter gold)
    inset = int(size * 0.10)
    draw.ellipse(
        (inset, inset, size - 1 - inset, size - 1 - inset),
        fill=(196, 164, 92, 255),
    )

    # Center "T" text
    text = "T"
    font = None
    # Try a bolder system font first, fall back to default
    for font_name in ("DejaVuSans-Bold.ttf", "Arial.ttf"):
        try:
            font = ImageFont.truetype(font_name, int(size * 0.55))
            break
        except Exception:
            font = None
    if font is None:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2
    # Text in primary green for TEMER look
    draw.text((text_x, text_y), text, fill=(122, 155, 44, 255), font=font)

    return logo


def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b


def generate_qr(link: str, logo_image: Image.Image | None = None, primary_hex: str | None = None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)

    # Solid color modules on white background
    # If no valid color is provided, fall back to normal black QR
    if primary_hex:
        try:
            r, g, b = _hex_to_rgb(primary_hex)
            fill = (r, g, b)
        except Exception:
            fill = "black"
    else:
        fill = "black"

    img = qr.make_image(fill_color=fill, back_color="white").convert("RGBA")

    # If no logo was uploaded, return a plain QR (no center image)
    if logo_image is None:
        return img

    # Otherwise, overlay the uploaded logo in the center.
    # Keep it fairly small so the QR remains easy to scan.
    max_logo_size = int(min(img.size) * 0.18)
    logo_image = logo_image.convert("RGBA")
    # Contain the logo inside a square so tall logos don't cover too much
    inner_logo = ImageOps.contain(logo_image, (max_logo_size, max_logo_size), Image.LANCZOS)

    # Add a white rounded background behind the logo to keep the QR readable
    padding = int(max_logo_size * 0.12)
    bg_w = inner_logo.size[0] + padding * 2
    bg_h = inner_logo.size[1] + padding * 2
    logo_bg = Image.new("RGBA", (bg_w, bg_h), (0, 0, 0, 0))
    draw_bg = ImageDraw.Draw(logo_bg)
    radius = int(min(bg_w, bg_h) * 0.3)
    draw_bg.rounded_rectangle(
        (0, 0, bg_w, bg_h),
        radius=radius,
        fill=(255, 255, 255, 255),
    )
    logo_bg.paste(inner_logo, (padding, padding), inner_logo)

    # Center the logo panel on the QR code
    pos = (
        (img.size[0] - logo_bg.size[0]) // 2,
        (img.size[1] - logo_bg.size[1]) // 2,
    )
    img.paste(logo_bg, pos, logo_bg)
    return img

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        filename = request.form['filename']
        # Optional custom HEX color; if empty, use plain black QR
        primary_hex = request.form.get('primary_hex') or None
        logo_image = None
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename:
            try:
                logo_bytes = logo_file.read()
                logo_image = Image.open(io.BytesIO(logo_bytes))
            except Exception:
                logo_image = None

        img = generate_qr(url, logo_image, primary_hex)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename if filename.endswith('.png') else filename + '.png'
        )
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
