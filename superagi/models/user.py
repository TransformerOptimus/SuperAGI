from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from base_model import BaseModel
from db import engine,connectDB
from sqlalchemy.orm import sessionmaker

class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


# __________________DB execution

engine = connectDB()
print("Engine")
print()
Session = sessionmaker(bind=engine)
session = Session()
new_user = User(id=1,name="John Doe",email="test@gmail.com",password="password")
BaseModel.metadata.create_all(engine)
# Add the user to the session
session.add(new_user)

# Commit the transaction
session.commit()

# Close the session
session.close()