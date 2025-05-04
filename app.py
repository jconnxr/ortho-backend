from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env (local only)
load_dotenv()

app = Flask(__name__)
CORS(app)

# Securely load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# -------------------------------
# TRIAGE ENDPOINT
# -------------------------------
@app.route('/triage', methods=['POST'])
def triage():
    data = request.json
    injury_location = data.get('location', '').lower()
    pain_level = int(data.get('painlevel', 0))
    onset_time = data.get('onsetTime', '').lower()
    activity = data.get('activity', '').lower()

    # Very basic rule-based logic
    if pain_level >= 7:
        recommendation = "Visit urgent care or see a doctor immediately."
    elif "swelling" in onset_time or pain_level >= 5:
        recommendation = "Rest and monitor your condition closely. Consider virtual consult."
    else:
        recommendation = "Self-care and monitor symptoms."

    assessment = f"Pain at {injury_location} during '{activity}' starting {onset_time}."

    return jsonify({
        "assessment": assessment,
        "recommendation": recommendation
    })

# -------------------------------
# CHATGPT AI FOLLOW-UP ENDPOINT
# -------------------------------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    try:
        response = openai.ChatCompletion.create(
         model='gpt-3.5-turbo',   
            messages=[
                {"role": "system", "content": "You are an orthopedic assistant helping a user after an injury. Ask helpful, medically relevant follow-up questions."},
                {"role": "user", "content": user_message}
            ]
        )
        return jsonify({"response": response['choices'][0]['message']['content']})
    except Exception as e:
        print("OpenAI error:", e)
        return jsonify({"error": "Something went wrong."}), 500

# -------------------------------
# OPTIONAL IMAGE UPLOAD ROUTE
# -------------------------------
@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    file.save(os.path.join('uploads', file.filename))
    return jsonify({'message': 'Image uploaded successfully'})

# -------------------------------
# MAIN
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
