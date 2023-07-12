from sqlalchemy import Column, Integer, Text, String

from superagi.models.base_model import DBBaseModel


class KnowledgeConfig(DBBaseModel):
    """
    Knowledge related configurations such as model, data_type, tokenizer, chunk_size, chunk_overlap, text_splitter, etc. are stored here.

    Attributes:
        id (int): The unique identifier of the knowledge configuration.
        knowledge_id (int): The identifier of the associated knowledge.
        key (str): The key of the configuration setting.
        value (str): The value of the configuration setting.
    """

    __tablename__ = 'knowledge_config'

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
    
    @classmethod
    def get_knowledge_config(cls, session, knowledge_id: int, knowledge):
        knowledge_configs = session.query(KnowledgeConfig).filter(KnowledgeConfig.knowledge_id == knowledge_id).all()
        for config in knowledge_configs:
            knowledge[config.key] = config.value

        return knowledge
    
    @classmethod
    def add_knowledge_config(cls, session, knowledge_id, knowledge_config):
        for key in knowledge_config.keys():
            config = KnowledgeConfig(knowledge_id=knowledge_id,key=key,value=knowledge_config[key])
            session.add(config)
            session.commit()
    