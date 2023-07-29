from superagi.helper.twitter_tokens import TwitterTokens
from superagi.models.db import connect_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = connect_db()
Session = sessionmaker(bind=engine)
tool_creds = TwitterTokens(Session()).get_twitter_creds(33)
print(tool_creds)