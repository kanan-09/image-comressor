import os
import zipfile
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO

app = Flask("CEJS")
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'compressed'
ZIP_NAME = 'compressed_images.zip'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_images():
    uploaded_files = request.files.getlist('images')
    compressed_paths = []

    for file in uploaded_files:
        if file.filename == '':
            continue

        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        # Сохраняем загруженный файл
        file.save(input_path)

        # Открываем изображение
        image = Image.open(input_path)

        # Конвертируем в RGB, если это PNG с прозрачностью или другой режим
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Сжимаем и сохраняем изображение
        image.save(output_path, "JPEG", quality=85, optimize=True)

        compressed_paths.append(output_path)

    # Создаем ZIP-архив
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for path in compressed_paths:
            zipf.write(path, os.path.basename(path))
    zip_buffer.seek(0)

    # Возвращаем сам ZIP-файл для скачивания через JS
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=ZIP_NAME
    )

if __name__ == '__main__':
    app.run(debug=True)
