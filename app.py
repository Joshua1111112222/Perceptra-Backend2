from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for demonstration purposes
data_store = []

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    # Add timestamp metadata if not already present
    if '_savedAt' not in data:
        data['_savedAt'] = datetime.utcnow().isoformat() + 'Z'  # ISO format with UTC
    data_store.append(data)
    return jsonify({"status": "success", "message": "Data submitted successfully!"})

@app.route('/rankings', methods=['GET'])
def rankings():
    # Calculate average score and highest score for each team
    rankings_data = []
    for entry in data_store:
        # Convert all ratings to integers (handle empty strings)
        try:
            defense = int(entry.get('defense', 0))
            strategy = int(entry.get('strategy', 0))
            effectiveness = int(entry.get('effectiveness', 0))
            driveSkill = int(entry.get('driveSkill', 0))
            scoring = int(entry.get('scoring', 0))
            consistency = int(entry.get('consistency', 0))
        except (ValueError, TypeError):
            # If conversion fails, use 0 as default
            defense = strategy = effectiveness = driveSkill = scoring = consistency = 0
        
        avg_score = (defense + strategy + effectiveness + driveSkill + scoring + consistency) / 6
        highest_score = max(defense, strategy, effectiveness, driveSkill, scoring, consistency)
        
        rankings_data.append({
            "matchNumber": entry.get('matchNumber', 'N/A'),
            "event": entry.get('event', 'N/A'),
            "teamName": entry.get('teamName', 'N/A'),
            "teamNumber": entry.get('teamNumber', 'N/A'),
            "avgScore": round(avg_score, 2),
            "highestScore": highest_score,
            "username": entry.get('username', 'Unknown'),
            "defense": defense,
            "strategy": strategy,
            "effectiveness": effectiveness,
            "driveSkill": driveSkill,
            "scoring": scoring,
            "consistency": consistency,
            "notes": entry.get('notes', ''),
            "_savedAt": entry.get('_savedAt', 'Unknown')  # Include the save timestamp
        })

    # Sort rankings_data by avgScore in descending order
    rankings_data.sort(key=lambda x: x['avgScore'], reverse=True)

    return jsonify(rankings_data)

@app.route('/delete', methods=['POST'])
def delete():
    data = request.json
    team_number = data.get('teamNumber')  # Use teamNumber as a unique identifier

    # Find and remove the entry from data_store
    global data_store
    data_store = [entry for entry in data_store if entry.get('teamNumber') != team_number]

    return jsonify({"status": "success", "message": "Entry deleted successfully!"})

@app.route('/clear', methods=['POST'])
def clear():
    global data_store
    data_store = []
    return jsonify({"status": "success", "message": "History cleared!"})

if __name__ == '__main__':
    app.run(debug=True)