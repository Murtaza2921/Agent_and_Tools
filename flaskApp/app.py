from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

# Directory for uploaded files
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Home route to render HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling document uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    # Simulate adding to knowledge base
    try:
        response = requests.post(
            "http://127.0.0.1:8000/upload", 
            files={"file": open(file_path, "rb")}
        )
        if response.status_code == 200:
            return jsonify({"message": f"File '{file.filename}' added to the knowledge base!"}), 200
        else:
            return jsonify({"message": "Failed to add file to knowledge base."}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Route for handling chatbot queries
@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get("query")
    if user_query:
        try:
            # Simulate chatbot response
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={"query": user_query}
            )
            print('api response :', response)
            bot_reply = response.json().get("response", "Sorry, something went wrong!")
            return jsonify({"response": bot_reply}), 200
        except Exception as e:
            return jsonify({"response": f"Error: {str(e)}"}), 500
    return jsonify({"response": "No query provided."}), 400

if __name__ == '__main__':
    app.run(debug=True)
