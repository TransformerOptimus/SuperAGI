from sqlalchemy import create_engine
from superagi.config.config import get_config
from superagi.lib.logger import logger

database_url = get_config('POSTGRES_URL')
db_username = get_config('DB_USERNAME')
db_password = get_config('DB_PASSWORD')
db_name = get_config('DB_NAME')

engine = None


def connect_db():
    """
    Connects to the PostgreSQL database using SQLAlchemy.

    Returns:
        engine: The SQLAlchemy engine object representing the database connection.
    """

    global engine
    if engine is not None:
        return engine

    # Create the connection URL
    if db_username is None:
        db_url = f'postgresql://{database_url}/{db_name}'
    else:
        db_url = f'postgresql://{db_username}:{db_password}@{database_url}/{db_name}'

    # Create the SQLAlchemy engine
    engine = create_engine(db_url,
                           pool_size=20,  # Maximum number of database connections in the pool
                           max_overflow=50,  # Maximum number of connections that can be created beyond the pool_size
                           pool_timeout=30,  # Timeout value in seconds for acquiring a connection from the pool
                           pool_recycle=1800,  # Recycle connections after this number of seconds (optional)
                           pool_pre_ping=False,  # Enable connection health checks (optional)
                           )

    # Test the connection
    try:
        connection = engine.connect()
        logger.info("Connected to the database! @ " + db_url)
        connection.close()
    except Exception as e:
        logger.error(f"Unable to connect to the database:{e}")
    return engine
