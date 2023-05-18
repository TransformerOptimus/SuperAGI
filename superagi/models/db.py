from sqlalchemy import create_engine

# Replace 'username' and 'password' with your PostgreSQL credentials
db_username = ''
db_password = ''
db_name = ''

engine = None

def connectDB():
    # Create the connection URL
    db_url = f'postgresql://{db_username}:{db_password}@localhost/{db_name}'

    # Create the SQLAlchemy engine
    global engine 
    engine = create_engine(db_url)

    # Test the connection
    try:
        connection = engine.connect()
        print("Connected to the database!")
        connection.close()
    except Exception as e:
        print("Unable to connect to the database:", e)
    return engine

# def getSession():