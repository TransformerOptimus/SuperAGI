# from sqlalchemy import Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base

# from base_model import DBBaseModel


# class LLM(DBBaseModel):
#     __tablename__ = 'llms'

#     id = Column(Integer, primary_key=True)
#     company = Column(String)
#     model_name = Column(String)
#     max_tokens = Column(Integer)
#     temperature = Column(Integer)
#     top_p = Column(Integer)
#     prompt = Column(String)
#     number_of_results = Column(Integer)
#     frequency_penalty = Column(Integer)
#     presence_penalty = Column(Integer)

#     def __repr__(self):
#         return f"LLM(id={self.id}, company='{self.company}', model_name='{self.model_name}', " \
#                f"max_tokens={self.max_tokens}, temperature={self.temperature}, top_p={self.top_p}, " \
#                f"prompt='{self.prompt}', number_of_results={self.number_of_results}, " \
#                f"frequency_penalty={self.frequency_penalty}, presence_penalty={self.presence_penalty})"