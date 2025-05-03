from flask import Flask, request, jsonify, session
from src.db_interface import NaC_DB_Interface
from src.embedding_interface import EmbeddingInterface
from flask_cors import CORS, cross_origin

def create_app_instance():
    app = Flask(__name__)
    app.secret_key = 'brunoschmuno'

    ROUND_COUNT = 8

    # Initialize the database
    with app.app_context():
        db_interface = NaC_DB_Interface()
        embedding_interface = EmbeddingInterface()


    # THIS SHOULD BE THE MAIN ENTRY POINT.
    @app.route("/getSwipes", methods=['GET'])
    @cross_origin()
    def question():

        user_id = request.args.get('user_id')

        movies_swiped = db_interface.get_user_movie_ids(user_id)
        
        if len(movies_swiped) < ROUND_COUNT:

            if not embedding_interface.user_embed_exists(user_id):
                embedding_interface.add_user_to_embeds(user_id)

            movies = embedding_interface.get_next_question_movie(movies_swiped)

            for movie in movies:
                db_interface.add_user_movie_pair(user_id, movie)

            return jsonify({"movies": movies}), 200

        else:
            return jsonify({"movies": []}), 200
        
    @app.route("/postSwipe", methods=['POST'])
    @cross_origin()
    def process_answer():

        if "user_id" not in request.args:
            return (jsonify({"message": "user_id not defined"}), 403)
        
        user_id = request.args.get('user_id')

        try:

            data = request.get_json()

            rating = data["rating"]
            movie_id = data["movie_id"]

        except Exception as e:
            return (jsonify({"message:" "Could not parse POST body (rating or film_id)"}), 401)

        if not db_interface.movie_exists(movie_id):
            return (jsonify({"message:" "Movie not found."}), 404)
        
        
        movies_swiped = db_interface.get_user_movie_ids(user_id)

        if len(movies_swiped) == 0:
            return ("Start off by sending a question request.", 503)
        
        if len(movies_swiped) < ROUND_COUNT:
            if rating != "skip": # skip when liked = 0
                embedding_interface.calculate_new_embedding(user_id, movie_id, rating)

            return jsonify({"message": "success", "swiped left" : ROUND_COUNT - len(movies_swiped) }), 200

        else: 
            return jsonify({"error": "Too many answers"}), 503
        

    @app.route("/getRecommendations", methods=['GET'])
    @cross_origin()
    def getRecommendations():
        group_id = request.args.get('group_id')

        if not group_id:
            return jsonify({"error": "group_id is required"}), 400

        if not db_interface.group_exists(group_id):
            return jsonify({"error": "group_id doesn't exist"}), 404

        user_ids = db_interface.get_users_in_group(group_id)
        movies = embedding_interface.calculate_users_shared_movies(user_ids)

        return jsonify({"movies": movies})

    @app.route("/health")
    @cross_origin()
    def health():
        return jsonify({"message" : "I am ALIVE"}), 200

    @app.route("/joinGroup", methods=['GET'])
    @cross_origin()
    def joinGroup():# -> tuple[Any, Literal[400]] | tuple[Any, Literal[404]] | tuple...:
        group_id = request.args.get('group_id')
        user_id = request.args.get('user_id')

        if not group_id or not user_id:
            return jsonify({"error": "group_id and user_id are required"}), 400

        if not db_interface.group_exists(group_id):
            return jsonify({"error": "Group not found"}), 404

        try:
            db_interface.add_user_to_group(user_id, group_id)
            return jsonify({"message": "User added to group successfully"}), 200
        except Exception as e:
            return jsonify({"error": "Error adding user."}), 500


    @app.route("/createGroup", methods=['POST'])
    @cross_origin()
    def createGroup():

        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "group_id and user_id are required"}), 400

        group_id = db_interface.create_group()

        if group_id == -1:
            return jsonify({"error": "Group could not be created."}), 500
        
        db_interface.add_user_to_group(user_id, group_id)
        return (jsonify(group_id), 200)
    
    @app.route("/getMovieInfo", methods=['GET'])
    @cross_origin()
    def getMovieInfo():

        if "movie_id" not in request.args:
            return (jsonify({"error" : "movie_id not defined"}), 400)

        try: 
            movie_id = int(request.args.get('movie_id'))
        except Exception as e:
            return (jsonify({"error" : "movie_id could not be parsed."}), 400)

        if not db_interface.movie_exists(movie_id):
            return (jsonify({"error" : "movie_id doesn't exist."}), 400)
        
        try:
            movie_info = db_interface.get_movie_info(movie_id)
            return jsonify(movie_info), 200
        
        except Exception as e:
            return (jsonify({"error" : e}), 400)

    return app