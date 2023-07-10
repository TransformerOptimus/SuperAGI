from sqlalchemy import Column, Integer, Text, String

from superagi.models.base_model import DBBaseModel


class VectorIndexConfig(DBBaseModel):
    """
    Index related configurations such as api_key and dimensions are stored here.

    Attributes:
        id (int): The unique identifier of the knowledge configuration.
        vector_index_id (int): The identifier of the associated vector index.
        key (str): The key of the configuration setting.
        value (str): The value of the configuration setting.
    """

    __tablename__ = 'vector_index_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vector_index_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the Vector Index Configuration object.

        Returns:
            str: String representation of the Vector Index Configuration.

        """
        return f"VectorIndexConfiguration(id={self.id}, knowledge_id={self.vector_index_id}, key={self.key}, value={self.value})"
    
    @classmethod
    def add_vector_index_config(cls, session, vector_index_id, key, value):
        index_config = VectorIndexConfig(vector_index_id=vector_index_id, key=key, value=value)
        session.add(index_config)
        session.commit()

    @classmethod
    def delete_vector_index_config(cls, session, vector_index_id):
        session.query(VectorIndexConfig).filter(VectorIndexConfig.vector_index_id == vector_index_id).delete()
        session.commit()
    
    @classmethod
    def get_index_state(cls, session, vector_index_id):
        index_config = session.query(VectorIndexConfig).filter(vector_index_id == vector_index_id, VectorIndexConfig.key == "INDEX_STATE").first()
        return index_config.value
