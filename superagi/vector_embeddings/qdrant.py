from superagi.vector_embeddings.base import VectorEmbeddings

class Qdrant(VectorEmbeddings):

    def __init__(self, uuid, embeds, metadata):
        self.uuid = uuid
        self.embeds = embeds
        self.metadata = metadata

    def get_vector_embeddings_from_chunks(self):
        """ Returns embeddings for vector dbs from final chunks"""
        return {'ids': self.uuid, 'payload': self.metadata, 'vectors': self.embeds}
