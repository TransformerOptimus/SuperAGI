from sqlalchemy import Column, Integer, Text, String

from superagi.models.base_model import DBBaseModel


class KnowledgeConfigs(DBBaseModel):
    """
    Knowledge related configurations such as model, data_type, tokenizer, chunk_size, chunk_overlap, text_splitter, etc. are stored here.
    Attributes:
        id (int): The unique identifier of the knowledge configuration.
        knowledge_id (int): The identifier of the associated knowledge.
        key (str): The key of the configuration setting.
        value (str): The value of the configuration setting.
    """

    __tablename__ = 'knowledge_configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledge_id = Column(Integer)
    key = Column(String)
    value = Column(Text)

    def __repr__(self):
        """
        Returns a string representation of the Knowledge Configuration object.
        Returns:
            str: String representation of the Knowledge Configuration.
        """
        return f"KnowledgeConfiguration(id={self.id}, knowledge_id={self.knowledge_id}, key={self.key}, value={self.value})"