from sqlalchemy.orm import Session

class PineconeHelper:
    
    def __init__(self, session):
        self.session = session
    
    def get_dimensions(self, vector_index):
        return "abc"
    
    def get_pinecone_index_state(self, vector_index):
        return "abc"