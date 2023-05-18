from db import engine,connectDB
from base_model import DBBaseModel
from sqlalchemy.orm import sessionmaker

from organisation import Organisation
from project import Project
from user import User
from organisation_users import OrganisationUser
from agent import Agent
# from tool import Tool
# from llm import LLM
# __________________DB execution

engine = connectDB()
print("Engine")
print()
DBBaseModel.metadata.create_all(engine)
# Organisation.__table__.create(bind=engine)
# Project.__table__.create(bind=engine)


Session = sessionmaker(bind=engine)
session = Session()
# new_user = User(id=1,name="John Doe",email="test@gmail.com",password="password")
# org1 = Organisation(
#     name="TestOrg1"
# )
# org2 = Organisation(
#     name="TestOrg2"
# )
# organisation_user1 = OrganisationUser(
#     user = new_user,
#     organisations = org1
# )

# organisation_user2 = OrganisationUser(
#     user = new_user,
#     organisations = org2
# )


# # Add the user to the session
# # session.add(org2)
# session.add_all([org1,org2])
# session.add_all([new_user])
# session.add_all([organisation_user1,organisation_user2])

# project1 = Project(
#     name = "Project1",
#     organisations=org2
# )
# project2 = Project(
#     name = "Project2",
#     organisations=org2
# )

# session.add_all([project1,project2])

# agent1 = Agent(
#     name = "Agent1",
#     project = project1,
#     description = "Testing Agent 1"
# )

# session.add_all(agent1)
# tool1 = Tool(
#     name = "Tool1",
#     description= "Testing tool1"
# )
# tool2 = Tool(
#     name = "Tool1",
#     description= "Testing tool1"
# )

email_to_find = "test@gmail.com"
user = session.query(User).filter(User.email == email_to_find).first()

# user = session.query(User).filter_by(User.email ==  "test@gmail.com").first()

if user:
    print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}")
else:
    print("User not found")





# Commit the transaction
session.commit()

# print(project1.organisations)
# print(org2.projects)

# Close the session
session.close()