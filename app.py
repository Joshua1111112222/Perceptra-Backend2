from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize storage at module level
data_store = []
leaderboard_store = []

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
            "_savedAt": entry.get('_savedAt', 'Unknown')
        })

    # Sort rankings_data by avgScore in descending order
    rankings_data.sort(key=lambda x: x['avgScore'], reverse=True)

    return jsonify(rankings_data)

@app.route('/delete', methods=['POST'])
def delete():
    data = request.json
    saved_at = data.get('_savedAt')  # Use _savedAt as a unique identifier

    if not saved_at:
        return jsonify({"status": "error", "message": "_savedAt is required"}), 400

    # Find and remove the entry from data_store
    global data_store
    data_store = [entry for entry in data_store if entry.get('_savedAt') != saved_at]

    return jsonify({"status": "success", "message": "Entry deleted successfully!"})

@app.route('/clear', methods=['POST'])
def clear():
    global data_store
    data_store = []
    return jsonify({"status": "success", "message": "History cleared!"})

# Cookie Clicker Leaderboard Endpoints
@app.route('/leaderboard/submit', methods=['POST'])
def submit_leaderboard():
    global leaderboard_store
    data = request.json
    
    # Validate required fields
    if not all(key in data for key in ['username', 'score']):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    # Ensure score is an integer (not float)
    try:
        data['score'] = int(float(data['score']))  # First convert to float then to int
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Score must be a number"}), 400
    
    # Trim and validate username
    data['username'] = data['username'].strip()
    if not data['username']:
        return jsonify({"status": "error", "message": "Username cannot be empty"}), 400
    
    # Add timestamp
    data['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    
    # Find existing entry
    existing_index = next((i for i, entry in enumerate(leaderboard_store) 
                        if entry['username'] == data['username']), None)
    
    if existing_index is not None:
        # Always replace if new score is higher
        if data['score'] > leaderboard_store[existing_index]['score']:
            leaderboard_store[existing_index] = data
    else:
        leaderboard_store.append(data)
    
    # Keep only top 100 scores
    leaderboard_store = sorted(leaderboard_store, key=lambda x: x['score'], reverse=True)[:100]
    
    return jsonify({
        "status": "success", 
        "message": "Score submitted successfully!",
        "score": data['score'],
        "username": data['username']
    })

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    global leaderboard_store
    # Return top 50 scores sorted by score (descending)
    sorted_leaderboard = sorted(leaderboard_store, key=lambda x: x['score'], reverse=True)[:50]
    return jsonify(sorted_leaderboard)

@app.route('/leaderboard/clear', methods=['POST'])
def clear_leaderboard():
    global leaderboard_store
    leaderboard_store = []
    return jsonify({"status": "success", "message": "Leaderboard cleared!"})

if __name__ == '__main__':
    app.run(debug=True)