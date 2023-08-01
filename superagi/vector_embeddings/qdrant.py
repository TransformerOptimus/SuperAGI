from typing import Any
from superagi.vector_embeddings.base import VectorEmbeddings

class Qdrant(VectorEmbeddings):

    def __init__(self, uuid, embeds, metadata):
        self.uuid = uuid
        self.embeds = embeds
        self.metadata = metadata

    def get_vector_embeddings_from_chunks(self):
        """ Returns embeddings for vector dbs from final chunks"""
        result = {}
        result['ids'] = self.uuid
        result['payload'] = self.metadata
        result['vectors'] = self.embeds

        return result