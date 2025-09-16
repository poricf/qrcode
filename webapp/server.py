from flask import Flask, render_template, request, send_file
import io
import qrcode

app = Flask(__name__)

def generate_qr(link: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="transparent")
    return img

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        filename = request.form['filename']
        img = generate_qr(url)
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
