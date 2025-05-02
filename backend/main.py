from database import app as db
from flask import Flask, request, jsonify
from database import db, User, UserGroups
from uuid import uuid4

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/postSwipes", methods=['POST'])
def postSwipes():
    data = request.get_json()
    
    # Check if user_id is provided in the request
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    # Check if user exists in database
    user = User.query.filter_by(user_id=user_id).first()
    
    # If user doesn't exist, create a new user
    if not user:
        new_user = User(user_id=user_id, embedding=[])  # Empty embedding for new user
        db.session.add(new_user)
        db.session.commit()
    
    swipes = data.get('swipes', [])

    return

@app.route("/getRecommendations", methods=['POST'])
def getRecommendations():

    group_id = request.get_json().get('group_id')

    # Query the UserGroups table for the given group_id
    user_group = UserGroups.query.filter_by(group_id=group_id).first()

    if not user_group:
        return jsonify({"error": "Group not found"}), 404

    # Retrieve the user IDs from the group
    user_ids = user_group.user_ids

    # Retrieve embeddings for each user ID
    embeddings = {}
    for user_id in user_ids:
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            embeddings[user_id] = user.embedding

    films = []  # Placeholder for further processing using user_ids

    return jsonify({
        "films": films
    })

@app.route("/getSwipes", methods=['POST'])
def getSwipes():

    user_id = request.get_json()

    film = []

    return jsonify({
        "film": film
    })

@app.route("/joinGroup", methods=['POST'])
def joinGroup():
    data = request.get_json()

    # Extract group_id and user_id from the request
    group_id = data.get('group_id')
    user_id = data.get('user_id')

    if not group_id or not user_id:
        return jsonify({"error": "group_id and user_id are required"}), 400

    # Query the UserGroups table for the given group_id
    user_group = UserGroups.query.filter_by(group_id=group_id).first()

    if not user_group:
        return jsonify({"error": "Group not found"}), 404

    # Add the user_id to the group if not already present
    if user_id not in user_group.user_ids:
        user_group.user_ids.append(user_id)
        db.session.commit()

    return jsonify({"message": "User added to group successfully", "group_id": group_id, "user_id": user_id})

@app.route("/createGroup", methods=['POST'])
def createGroup():
    data = request.get_json()

    # Extract user_id from the request
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # Auto-generate a unique group_id
    group_id = str(uuid4())

    # Create a new group with the user as the first member
    new_group = UserGroups(group_id=group_id, user_ids=[user_id])
    db.session.add(new_group)
    db.session.commit()

    user_group = UserGroups.query.filter_by(group_id=group_id).first()
    if not user_group:
        return jsonify({"error": "Group not found"}), 404


    return jsonify({"message": "Group created successfully", "group_id": group_id, "user_id": user_id})