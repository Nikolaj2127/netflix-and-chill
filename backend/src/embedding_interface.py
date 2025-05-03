from qdrant_client import QdrantClient
from qdrant_client.http import models
import random

class EmbeddingInterface:
    def __init__(self):
        self.client = QdrantClient(url="http://tobias-home.hindahl.de:6333/", api_key="check24")
        self.EMBEDDING_DIMENSIONS = 3072

        self.user_embeds = None # TODO.


    def get_next_question_movie(self, past_swipes):
        """
            Returns the next movie to ask. This might be dependant on the round we are on. past swipes is list of ints
        """
        context = [models.ContextPair(positive=(random.randint(1, 250)), negative=i) for i in past_swipes]
        if not past_swipes:
            limit = 2
        else:
            limit = 1

        discover_queries = [
            models.QueryRequest(
                query=models.ContextQuery(
                    context=context,
                ),
                limit=limit,
            ),
        ]

        results = self.client.query_batch_points(
            collection_name="movies", requests=discover_queries
        )

        p = [i.points for i in results]

        return [i.id for i in p[0]]


    def fetch_embedding_from_movie(self, movie):
        """
            Searches through the vector database and returns the embedding for a specifc movie.
        """
        pass
    

    def calculate_new_embedding(self, embedding, movie, liked):
        """
            Calculates the new embedding based off of the current embedding and the movie.
        """

        m_embed = self.fetch_embedding_from_movie(movie)

        if m_embed is None:
            return embedding
        else:
            # Change the embedding based on liked or not.
            m_embed = m_embed if liked else -.3 * m_embed 
            if embedding: 
                return embedding + m_embed
            else:
                return m_embed

    def add_user_to_embeds(self, user_id):
        """
            Adds a user with a uuid to the vectorstore. Inits at Zero-Vector.
        """
        pass


    def user_in_enbeds(self, user_id):
        """
            Returns true if user is in the enbedded db.
        """
        pass

    def calculate_users_shared_movies(self, user_ids):
        """
        This is the whole point of the program. We take the user_ids, query the embedded databases and return the shared interested movies.
        """
        pass