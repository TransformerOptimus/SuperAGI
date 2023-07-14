import os
import pika

def test_connection():
    # Retrieve the values from environment variables
    rabbitmq_server = os.getenv('RABBITMQ_SERVER', 'host.docker.internal')
    rabbitmq_username = os.getenv('RABBITMQ_USERNAME', 'guest')
    rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')

    # Build connection parameters
    credentials = pika.PlainCredentials(rabbitmq_username, rabbitmq_password)
    connection_params = pika.ConnectionParameters(host=rabbitmq_server, credentials=credentials)

    try:
        # Try to establish a connection
        connection = pika.BlockingConnection(connection_params)
        
        # If successful, close the connection and return True
        connection.close()
        print("Connection to RabbitMQ server was successful!")
        return True
    except Exception as e:
        # If an error occurs, print the error and return False
        print(f"Failed to connect to RabbitMQ server: {e}")
        return False

if __name__ == "__main__":
    test_connection()
