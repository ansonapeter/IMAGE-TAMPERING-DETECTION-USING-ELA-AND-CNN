from flask import Flask, render_template, request, jsonify, url_for
from PIL import Image, ImageChops, ImageEnhance, ImageFilter
import os
import numpy as np
from datetime import datetime
from keras.models import load_model

app = Flask(__name__)

# Folders for uploads and processed images
UPLOAD_FOLDER = os.path.join("static", "uploads")
PROCESSED_FOLDER = os.path.join("static", "processed")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Load CNN model
MODEL_PATH = "model/model.h5"
model = load_model(MODEL_PATH, compile=False)  # 👈 added compile=False
IMG_SIZE = (128, 128)


def convert_to_ela_image(path, quality=90):
    """Convert an image to its ELA (Error Level Analysis) version with scaling fix."""
    temp_filename = os.path.join(PROCESSED_FOLDER, "temp_ela.jpg")
    ela_filename = os.path.join(
        PROCESSED_FOLDER,
        f"ela_{os.path.splitext(os.path.basename(path))[0]}.jpg"
    )

    # Open original and save compressed copy
    image = Image.open(path).convert('RGB')
    image.save(temp_filename, 'JPEG', quality=quality)

    # Compute difference
    temp_image = Image.open(temp_filename)
    ela_image = ImageChops.difference(image, temp_image)

    # Calculate scaling while preventing extreme brightening
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        scale = 1
    else:
        scale = min(255.0 / max_diff, 8.0)

    # Apply scaling
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
    ela_image = ela_image.filter(ImageFilter.SMOOTH)
    ela_image.save(ela_filename, "JPEG")
    return ela_filename

def predict_image(image_path):
    """Predict if the image is real or fake using the trained model."""
    ela_img = convert_to_ela_image(image_path)
    img = Image.open(ela_img).resize(IMG_SIZE)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0][0]
    confidence = float(prediction)
    label = "Fake" if confidence > 0.5 else "Real"
    return label, round(confidence * 100, 2), ela_img

# 🏠 Homepage Route
@app.route("/")
def home():
    return render_template("home.html")  # You will create this template

# 📷 ELA Analysis Page
@app.route("/ela")
def ela_page():
    return render_template("index.html")  # Existing analyzer UI

@app.route("/preview", methods=["POST"])
def preview():
    if "image" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        filename = f"preview_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        path = os.path.join(UPLOAD_FOLDER, filename)

        img = Image.open(file).convert("RGB")
        img.save(path, "JPEG", quality=90)

        return jsonify({
            "preview_image": url_for("static", filename=f"uploads/{filename}") + f"?v={datetime.now().timestamp()}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        original_ext = os.path.splitext(file.filename)[1].lower()
        filename = datetime.now().strftime("%Y%m%d%H%M%S") + original_ext
        original_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(original_path)

        label, confidence, ela_path = predict_image(original_path)

        jpg_filename = os.path.splitext(filename)[0] + ".jpg"
        jpg_path = os.path.join(UPLOAD_FOLDER, jpg_filename)
        Image.open(original_path).convert("RGB").save(jpg_path, "JPEG", quality=90)

        return jsonify({
            "original_image": url_for("static", filename=f"uploads/{jpg_filename}") + f"?v={datetime.now().timestamp()}",
            "result": label,
            "confidence": confidence,
            "ela_image": url_for("static", filename=f"processed/{os.path.basename(ela_path)}") + f"?v={datetime.now().timestamp()}"
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "traceback": error_details
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
