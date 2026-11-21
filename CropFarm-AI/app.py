
import os
import uuid
import json
import numpy as np
import tensorflow as tf
from multilingual_disease_info import MULTILINGUAL_DISEASE_INFO, DISEASE_NAMES
from pdf_report import generate_pdf_report

from flask import Flask, render_template, request, session, redirect, url_for, send_file
from translations import TRANSLATIONS
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "CropFarm AI_language_key"
@app.context_processor
def inject_translations():
    language = session.get("language", "en")

    return {
        "t": TRANSLATIONS.get(language, TRANSLATIONS["en"]),
        "current_language": language
    }


@app.route("/set_language", methods=["POST"])
def set_language():
    language = request.form.get("language", "en")

    if language in TRANSLATIONS:
        session["language"] = language

    return redirect(request.referrer or url_for("scanner"))

# Project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

# Load trained AI model
MODEL_PATH = os.path.join(
    BASE_DIR, "models", "crop_disease_model.keras"
)

CLASS_PATH = os.path.join(
    BASE_DIR, "models", "class_indices.json"
)

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_PATH, "r") as file:
    class_indices = json.load(file)

# Convert class indices into disease names
class_names = {
    index: name for name, index in class_indices.items()
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# Predict crop disease
def predict_disease(image_path):

    image = tf.keras.utils.load_img(
        image_path,
        target_size=(128, 128)
    )

    image_array = tf.keras.utils.img_to_array(image)

    image_array = image_array / 255.0

    image_array = np.expand_dims(image_array, axis=0)

    predictions = model.predict(image_array, verbose=0)

    predicted_index = int(np.argmax(predictions[0]))

    disease_name = class_names[predicted_index]

    confidence = float(predictions[0][predicted_index]) * 100

    return disease_name, round(confidence, 2)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scanner", methods=["GET", "POST"])
def scanner():

    uploaded_image = None
    message = None
    predicted_disease = None
    confidence = None
    disease_details = None
    disease_display_name = None
    report_filename = None

    if request.method == "POST":

        if "crop_image" not in request.files:
            message = "Please select an image."

        else:
            file = request.files["crop_image"]

            if file.filename == "":
                message = "No image selected."

            elif not allowed_file(file.filename):
                message = "Please upload JPG, JPEG, PNG or WEBP."

            else:
                filename = secure_filename(file.filename)
                unique_name = uuid.uuid4().hex + "_" + filename

                image_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    unique_name
                )

                file.save(image_path)

                uploaded_image = unique_name

                try:
                    predicted_disease, confidence = predict_disease(
                        image_path
                    )
                    language = session.get("language", "en")

                    disease_display_name = DISEASE_NAMES.get(
                        language,
                        DISEASE_NAMES["en"]
                    ).get(
                        predicted_disease,
                        predicted_disease.replace("_", " ")
                    )

                    print("DEBUG - Predicted disease:", repr(predicted_disease))

                    language = session.get("language", "en")

                    language_disease_info = MULTILINGUAL_DISEASE_INFO.get(
                        language,
                        MULTILINGUAL_DISEASE_INFO["en"]
                    )

                    
                    disease_details = language_disease_info.get(
                        predicted_disease,
                        MULTILINGUAL_DISEASE_INFO["en"].get(predicted_disease)
                    )

        
                    try:
                        report_folder = os.path.join(
                            app.root_path, "reports"
                        )
                        os.makedirs(report_folder, exist_ok=True)

                        report_filename = uuid.uuid4().hex + ".pdf"
                        report_path = os.path.join(
                            report_folder, report_filename
                        )

                        pdf_buffer = generate_pdf_report(
                            image_path,
                            disease_display_name,
                            confidence,
                            disease_details,
                            language=session.get("language", "en")
                        )

                        with open(report_path, "wb") as report_file:
                            report_file.write(pdf_buffer.getvalue())

                    except Exception as pdf_error:
                        report_filename = None
                        print("PDF generation error:", pdf_error)

                    print("DEBUG DISEASE:", predicted_disease)
                    print("DEBUG DETAILS:", disease_details)

                    message = "Crop disease prediction completed!"

                except Exception as error:
                    message = "Unable to analyse this image. Please try another image."
                    print("Prediction error:", error)
        
    return render_template(
    "scanner.html",
    message=message,
    uploaded_image=uploaded_image,
    predicted_disease=predicted_disease,
    confidence=confidence,
    disease_display_name=disease_display_name,
        disease_details=disease_details,
    report_filename=report_filename
)

@app.route("/download_report/<filename>")
def download_report(filename):

    filename = secure_filename(filename)

    report_path = os.path.join(
        app.root_path,
        "reports",
        filename
    )

    if not os.path.isfile(report_path):
        return "Report not found.", 404

    return send_file(
        report_path,
        as_attachment=True,
        download_name="AgriVision_Diagnosis_Report.pdf"
    )
@app.route("/about")
def about():
    return "cropFarm AI - Multi-Crop Disease Detection System"


if __name__ == "__main__":
    app.run(debug=True)
