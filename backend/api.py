from flask import Flask, jsonify
from flask_pymongo import PyMongo

# This is needed to allow a web browser (our future dashboard)
# to talk to this API from a different "origin" (domain/port).
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for our app

# --- Configuration ---
# Connect to our existing database
app.config["MONGO_URI"] = "mongodb://localhost:27017/ids_dashboard"
mongo = PyMongo(app)

# --- API Endpoints ---
# This is the "web page" for our API

@app.route('/api/alerts', methods=['GET'])
def get_latest_alerts():
    """Get the 100 most recent alerts."""
    try:
        # Find alerts in the 'alerts' collection
        # Sort by timestamp descending (newest first)
        # Limit to 100 results
        alerts = mongo.db.alerts.find(
            {},  # Empty filter = match all
            {'_id': 0} # Projection: don't include the weird '_id' field
        ).sort('timestamp', -1).limit(100)

        # Convert the database data to a list and return it as JSON
        return jsonify(list(alerts)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats/total_alerts', methods=['GET'])
def get_total_alerts():
    """Get the total count of all alerts in the database."""
    try:
        count = mongo.db.alerts.count_documents({})
        return jsonify({"total_alerts": count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats/top_ips', methods=['GET'])
def get_top_ips():
    """Get the top 5 most frequent attacker IPs."""
    try:
        # This is a MongoDB "aggregation pipeline"
        # It's a fancy way of saying "Group by src_ip, count them, and sort"
        pipeline = [
            {"$group": {"_id": "$src_ip", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_ips = list(mongo.db.alerts.aggregate(pipeline))
        return jsonify(top_ips), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats/top_alerts', methods=['GET'])
def get_top_alerts():
    """Get the top 5 most frequent alert signatures."""
    try:
        pipeline = [
            {"$group": {"_id": "$alert.signature", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_alerts = list(mongo.db.alerts.aggregate(pipeline))
        return jsonify(top_alerts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run the API Server ---
if __name__ == '__main__':
    # Run on '0.0.0.0' to make it accessible from outside the VM
    # (handy for testing)
    # Changed debug=False for a cleaner startup message, can be set to True for development
    app.run(debug=False, host='0.0.0.0', port=5000)
