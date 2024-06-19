from flask import Flask, request, jsonify, render_template
import requests
import pytesseract
from PIL import Image
import io

app = Flask(__name__)

def extract_text_from_image(image_file):
    img = Image.open(image_file)
    # Perform OCR on the image
    text = pytesseract.image_to_string(img)
    return text

# Serve the HTML template for reports
@app.route('/reports', methods=['GET'])
def reports():
    return render_template('reports.html')

# Serve the HTML template for text input
@app.route('/text', methods=['GET'])
def text_simplifier():
    return render_template('text.html')

# Handle file upload, extract text, and send to FastAPI
@app.route('/upload-pdf/', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    try:
        # Extract text from image
        extracted_text = extract_text_from_image(file)
        
        # Send extracted text to FastAPI for simplification
        rest_api_url = 'http://localhost:8000/upload-text/'
        response = requests.post(rest_api_url, json={'medical_text': extracted_text})

        if response.status_code == 200:
            return jsonify({'simplified_text': response.json().get('simplified_text')})
        else:
            return jsonify({'error': 'Failed to get simplified text'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Handle text input and interaction with REST API
@app.route('/upload-text/', methods=['POST'])
def upload_text():
    data = request.get_json()
    medical_text = data.get('medical_text')

    if not medical_text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Replace with the actual URL of your REST API
        rest_api_url = 'http://localhost:8000/upload-text/'
        response = requests.post(rest_api_url, json={'medical_text': medical_text})

        if response.status_code == 200:
            return jsonify({'simplified_text': response.json().get('simplified_text')})
        else:
            return jsonify({'error': 'Failed to get simplified text'}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
