from superagi.tools.rabbitmq.rabbitmq_tool import RabbitMQTool

# You should provide a valid configuration object for RabbitMQTool
config = {
    'rabbitmq_server': 'localhost',
    'rabbitmq_username': 'guest',
    'rabbitmq_password': 'guest',
}
tool = RabbitMQTool(**config)
tool._execute(tool_input={"operation": "send_message", "receiver": "hello", "message": "Hello World!"})
