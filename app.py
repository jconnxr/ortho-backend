from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/triage-ai', methods=['POST'])
def triage_ai():
    data = request.json

    # Intake Data
    age = int(data.get('age', 0))
    body_part = data.get('bodyPart', '').lower()
    weight_bearing = data.get('weightBearing', '').lower()
    neuro_symptoms = data.get('neuroSymptoms', '').lower()
    deformity = data.get('deformity', '').lower()
    joint_movement = data.get('jointMovement', '').lower()
    swelling_level = data.get('swellingLevel', '').lower()
    open_wounds = data.get('openWounds', '').lower()
    night_pain = data.get('nightPain', '').lower()
    image_data = data.get('image', None)

    # Rule-Based Logic
    if deformity == 'yes' or open_wounds == 'yes' or night_pain == 'yes':
        rule_result = "🚨 Emergency: Go to the nearest Emergency Department or call 911."
    elif neuro_symptoms != 'none' and body_part in ['neck', 'spine']:
        rule_result = "🚨 Emergency: Possible spinal involvement. Seek immediate ER evaluation."
    elif body_part == 'ankle' and weight_bearing == 'not at all':
        rule_result = "📋 Ottawa Ankle Rule triggered. Recommend urgent imaging at an Urgent Care or Radiology Center."
    elif weight_bearing == 'not at all':
        rule_result = "📋 Unable to bear weight. Urgent Care evaluation recommended."
    elif swelling_level in ['severe', 'high'] or joint_movement == 'none':
        rule_result = "📋 Moderate concern. Visit Urgent Care if symptoms worsen or persist beyond 24 hours."
    else:
        rule_result = "✅ No critical issues detected. Recommend home care, rest, and monitor symptoms."
    ai_prompt = f"""Patient Info:
Age: {age}
Injury Area: {body_part.capitalize()}.
Symptoms:
- Joint Movement: {joint_movement}
- Weight Bearing: {weight_bearing}
- Neuro Symptoms: {neuro_symptoms}
- Deformity: {deformity}
- Swelling Level: {swelling_level}
- Open Wounds: {open_wounds}
- Night Pain: {night_pain}

Recommendation: {rule_result}

Compose a supportive, clear, and empathetic response for the patient explaining the recommendation and next steps. Keep it under 150 words and avoid medical jargon."""

    try:
        text_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a compassionate orthopedic assistant."},
                {"role": "user", "content": ai_prompt}
            ]
        )
        ai_response = text_response.choices[0].message.content.strip()

        # AI Image Analysis Using New API Format
        if image_data:
            image_prompt = (
                "You are reviewing an image of a physical injury. "
                "Assess and describe if there are any visible signs of swelling, bruising, open wounds, bleeding, skin discoloration, or obvious deformity. "
                "Respond clearly and concisely under 100 words. Do not provide a diagnosis, only describe visible findings."
            )
            vision_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": image_prompt},
                            {"type": "image_url", "image_url": {"url": image_data}}
                        ]
                    }
                ]
            )
            image_assessment = vision_response.choices[0].message.content.strip()
        else:
            image_assessment = "No image provided for analysis."

        return jsonify({
            "assessment": f"Injury to {body_part.capitalize()}. Movement: {joint_movement}. Weight Bearing: {weight_bearing}.",
            "rule_result": rule_result,
            "ai_response": ai_response,
            "image_assessment": image_assessment
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({
            "assessment": f"Injury to {body_part.capitalize()}.",
            "rule_result": rule_result,
            "ai_response": "Unable to generate AI response at this time.",
            "image_assessment": "Image analysis unavailable.",
            "error": str(e)
        })
if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.128')

