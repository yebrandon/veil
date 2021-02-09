import flask
import flask_cors
import base64
import os

import img_processor
import classifier

app = flask.Flask(__name__)
flask_cors.CORS(app)


def save_img(b64_str):
    """
    Saves image as file capture.png
    :param b64_str: base64 encoded string representation of image data
    """
    parsed_b64_str = b64_str.replace(b64_str[:22], "", 1)  # remove data tags
    img_data = base64.b64decode(parsed_b64_str)
    with open("capture.png", "wb") as img_file:
        img_file.write(img_data)


@app.route("/")
def home():
    return "Flask API is running!"


@app.route("/get-imgs")
def get_imgs():
    """
    Retrieves images in image directory
    :return JSON object with an entry for each image with its filename and base64 encoded string representation
    """
    results = {}
    for filename in os.listdir("./detected_faces"):
        with open("./detected_faces/" + filename, "rb") as image_file:
            encoded_bytes = base64.b64encode(image_file.read())
            encoded_str = encoded_bytes.decode("utf-8")
            results[filename] = encoded_str
    return flask.jsonify(results)


@app.route("/analyze-capture", methods=["POST"])
def analyze_capture():
    """
    Executes facial recognition processing and ML classification on image
    return: JSON object with an entry for each image with its filename, detection result, and confidence level
    """
    req_data = flask.request.get_json()
    save_img(req_data["b64Str"])
    img_processor.process_imgs()
    classifier.write_img_labels()
    return flask.send_file("results.json", mimetype="application/json")


if __name__ == "__main__":
    app.run(port=8000)