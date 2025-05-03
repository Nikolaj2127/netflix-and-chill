from qdrant_client import QdrantClient
from qdrant_client.http import models
import random
import numpy as np

class EmbeddingInterface:
    def __init__(self):
        self.client = QdrantClient(url="http://tobias-home.hindahl.de:6333/", api_key="check24")
        self.EMBEDDING_DIMENSIONS = 3072

        # Maps user_id to vector - not the prettiest, but it should work.
        self.user_embeds = map()


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
    
    def user_embed_exists(self, user_id):
        return user_id in self.user_embeds.keys()
        
    def fetch_embedding_from_user(self, user_id):
        if not self.user_embed_exists(user_id):
            raise RuntimeError("User doesn't exist.")
        
        return np.array(self.user_embeds[user_id])

    def calculate_new_embedding(self, user_id, movie, liked):
        """
            Calculates the new embedding based off of the current embedding and the movie.
        """

        m_embed = self.fetch_embedding_from_movie(movie)
        u_embed =  self.fetch_embedding_from_user(user_id)

        if m_embed is None:
            return
        else:
            # Change the embedding based on liked or not.
            m_embed = m_embed if liked else -.3 * m_embed 
            if u_embed: 
                self.user_embeds[user_id] = u_embed + m_embed
            else:
                self.user_embeds[user_id] = m_embed

    def add_user_to_embeds(self, user_id):
        """
            Adds a user with a uuid to the vectorstore. Inits at Zero-Vector.
        """
        self.user_embeds[user_id] = np.zeros(self.EMBEDDING_DIMENSIONS)

    def calculate_users_shared_movies(self, user_ids):
        """
        This is the whole point of the program. We take the user_ids, query the embedded databases and return the shared interested movies.

        TODO: with team.
        """
        vectors = []

        for user_id in user_ids:
            embedding = self.fetch_embedding_from_user.get(user_id)
            if embedding is not None:
                vectors.append(np.array(embedding))
            else:
                print(f"Warning: No embedding found for user_id {user_id}")

        combined_vector = np.mean(np.stack(vectors), axis=0)

        normalized_vector = self.sigmoid(combined_vector)

        results = self.client.client.query_points(
            collection_name="movies2", # TODO to be changed to "movies_top1000_1024"
            query=normalized_vector,
        )

        p = results.points

        re = [i.id for i in p]
        return re

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
