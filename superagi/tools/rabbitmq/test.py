import os
from superagi.tools.rabbitmq.rabbitmq_toolkit import RabbitMQTool

# Retrieve the values from environment variables
rabbitmq_server = os.getenv('RABBITMQ_SERVER', 'host.docker.internal')
rabbitmq_username = os.getenv('RABBITMQ_USERNAME', 'guest')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')

# Create an instance of the class, passing the retrieved values
tool = RabbitMQTool(rabbitmq_server=rabbitmq_server, rabbitmq_username=rabbitmq_username, rabbitmq_password=rabbitmq_password)

# Check that the attributes are correctly initialized
assert tool.rabbitmq_server == rabbitmq_server, f'Expected rabbitmq_server to be {rabbitmq_server}, but got {tool.rabbitmq_server}'
assert tool.rabbitmq_username == rabbitmq_username, f'Expected rabbitmq_username to be {rabbitmq_username}, but got {tool.rabbitmq_username}'
assert tool.rabbitmq_password == rabbitmq_password, f'Expected rabbitmq_password to be {rabbitmq_password}, but got {tool.rabbitmq_password}'

print('All attributes are correctly initialized!')
