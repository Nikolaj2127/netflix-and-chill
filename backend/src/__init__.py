from flask import Flask, request, jsonify, session
from src.db_interface import NaC_DB_Interface
from src.embedding_interface import EmbeddingInterface

def create_app_instance():
    app = Flask(__name__)
    app.secret_key = 'brunoschmuno'

    ROUND_COUNT = 8

    # Initialize the database
    with app.app_context():
        db_interface = NaC_DB_Interface()
        embedding_interface = EmbeddingInterface()


    # THIS SHOULD BE THE MAIN ENTRY POINT.
    @app.route("/getSwipe", methods=['GET'])
    def question():    

        user_id = request.args.get('userId')

        if "swiped" not in session:
            session["swiped"] = []

        if len(session["swiped"]) < ROUND_COUNT:

            if not embedding_interface.user_embed_exists(user_id):
                embedding_interface.add_user_to_embeds(user_id)

            movies = embedding_interface.get_next_question_movie(session["swiped"])
            session["swiped"] += movies

            return jsonify({"movies": movies}), 200

        else:
            return jsonify({"movies": []}), 200
        
    @app.route("/postSwipe", methods=['POST'])
    def process_answer():

        if "user_id" not in request.args:
            return (jsonify({"message": "user_id not defined"}), 403)
        
        user_id = request.args.get('user_id')

        try:
            print(request.data.get('rating'))
            print(request.data.get('film_id'))

            rating = int(request.values.get('liked'))
            movie_id = int(request.form.get('movie_id'))
        except Exception as e:
            return (jsonify({"message:" "Could not parse POST body (rating or film_id)"}), 401)

        if not db_interface.movie_exists(movie_id):
            return (jsonify({"message:" "Movie not found."}), 404)
        
        if "swiped" not in session:
            return ("Start off by sending a question request.", 503)
        
        if len(session["swiped"]) < ROUND_COUNT:
            if liked != 0: # skip when liked = 0
                embedding_interface.calculate_new_embedding(user_id, movie_id, liked)
                # TODO:
                # session["embedding"] = list(embedding_interface.calculate_new_embedding(session["embedding"], movie_id, liked))  

            return jsonify({"message": "success", "swiped left" : ROUND_COUNT - len(session["swiped"]) }), 200

        else: 
            return jsonify({"error": "Too many answers"}), 503
        

    @app.route("/getRecommendations", methods=['POST'])
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
    def health():
        return jsonify({"message" : "I am ALIVE"}), 200

    @app.route("/joinGroup", methods=['GET'])
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