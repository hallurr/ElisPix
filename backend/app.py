from flask import request
from flask import Flask
from image_processor import *
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config['DEBUG'] = True

if app.config['DEBUG']:
    CORS(app)


@app.route('/process', methods=['POST'])
def process_images():
    input_images = request.files.getlist("images")
    processor = ImageProcessor()
    output_images = processor.process_images(input_images)
    return jsonify({"status": "success", "images": output_images}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
