from db import engine,connectDB
from base_model import BaseModel
from sqlalchemy.orm import sessionmaker

from organisation import Organisation
from project import Project
# __________________DB execution

engine = connectDB()
print("Engine")
print()
# BaseModel.metadata.create_all(engine)
Organisation.__table__.create(bind=engine)
Project.__table__.create(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()
# new_user = User(id=1,name="John Doe",email="test@gmail.com",password="password")
org1 = Organisation(
    name="TestOrg1"
)
org2 = Organisation(
    name="TestOrg2"
)

# Add the user to the session
# session.add(org2)
session.add_all([org1,org2])
project1 = Project(
    name = "Project1",
    organisations=org2
)
project2 = Project(
    name = "Project2",
    organisations=org2
)

session.add_all([project1,project2])
# Commit the transaction
session.commit()

# print(project1.organisations)
# print(org2.projects)

# Close the session
session.close()