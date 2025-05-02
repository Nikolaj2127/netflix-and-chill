from flask import Flask, request, jsonify
from database import init_app, get_db_connection
from uuid import uuid4

app = Flask(__name__)

# Initialize the database
with app.app_context():
    init_app()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/postSwipe", methods=['POST'])
def postSwipe():
    swipe = request.get_json()
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    film_id = swipe.film_id
    film_rating = swipe.rating

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM User WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    embedding = {}
    cursor.execute("SELECT embedding FROM User WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        embedding = user['embedding']

    if not user:
        # Insert new user
        cursor.execute("INSERT INTO User (user_id, embedding) VALUES (?, ?)", (user_id, b""))
        conn.commit()

    conn.close()
    return jsonify({"message": "Swipes processed successfully"})

@app.route("/getSwipes")
def getSwipes():
    user_id = request.args.get('user_id')

    films =[]

    return jsonify({
        "films": films
    })

@app.route("/getRecommendations", methods=['POST'])
def getRecommendations():
    group_id = request.args.get('group_id')

    if not group_id:
        return jsonify({"error": "group_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query UserGroups table
    cursor.execute("SELECT user_ids FROM UserGroups WHERE group_id = ?", (group_id,))
    user_group = cursor.fetchone()

    if not user_group:
        conn.close()
        return jsonify({"error": "Group not found"}), 404

    user_ids = user_group['user_ids'].split(',')
    embeddings = {}

    for user_id in user_ids:
        cursor.execute("SELECT embedding FROM User WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            embeddings[user_id] = user['embedding']

    conn.close()
    return jsonify({"films": []})

@app.route("/joinGroup", methods=['POST'])
def joinGroup():
    group_id = request.args.get('group_id')
    user_id = request.args.get('user_id')

    if not group_id or not user_id:
        return jsonify({"error": "group_id and user_id are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query UserGroups table
    cursor.execute("SELECT user_ids FROM UserGroups WHERE group_id = ?", (group_id,))
    user_group = cursor.fetchone()

    if not user_group:
        conn.close()
        return jsonify({"error": "Group not found"}), 404

    user_ids = user_group['user_ids'].split(',')
    if user_id not in user_ids:
        user_ids.append(user_id)
        cursor.execute("UPDATE UserGroups SET user_ids = ? WHERE group_id = ?", (','.join(user_ids), group_id))
        conn.commit()

    conn.close()
    return jsonify({"message": "User added to group successfully"})

@app.route("/createGroup", methods=['POST'])
def createGroup():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    group_id = str(uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert new group
    cursor.execute("INSERT INTO UserGroups (group_id, user_ids) VALUES (?, ?)", (group_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Group created successfully", "group_id": group_id, "user_id": user_id})