from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/triage', methods=['POST'])
def triage():
    data = request.get_json()

    location = data.get('location', 'unknown')
    pain = int(data.get('painLevel', 0))
    onset = data.get('onsetTime', 'unspecified')
    activity = data.get('activity', 'unspecified')

    # Simple triage logic
    if pain >= 8:
        recommendation = "Seek urgent care or ER visit."
    elif pain >= 4:
        recommendation = "Schedule a telehealth visit."
    else:
        recommendation = "Self-care and monitor symptoms."

    assessment = f"Pain at {location} during '{activity}' starting {onset}."

    return jsonify({
        "assessment": assessment,
        "recommendation": recommendation
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
