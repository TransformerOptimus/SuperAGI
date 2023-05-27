from sqlalchemy import create_engine
from superagi.config.config import get_config

db_username = get_config('POSTGRES_USER')
db_password = get_config('POSTGRES_PASSWORD')
db_name = get_config('POSTGRES_DB')

engine = None

def connectDB():

    global engine
    if engine != None:
        print("Engine returned")
        return engine 

    # Create the connection URL
    db_url = f'postgresql://{db_username}:{db_password}@super__postgres/{db_name}'

    # Create the SQLAlchemy engine
    engine = create_engine(db_url)

    # Test the connection
    try:
        connection = engine.connect()
        print("Connected to the database! @ "+db_url)
        connection.close()
    except Exception as e:
        print("Unable to connect to the database:", e)
    return engine