# from sqlalchemy.orm import sessionmaker
# from superagi.models.db import connect_db
# from superagi.resource_manager.file_manager import FileManager
#
# #
# engine = connect_db()
# Session = sessionmaker(bind=engine)
# session = Session()
# # file_path = 'output/Village_Story.txt'
# # response = FileManager(session=session, agent_id=1, agent_execution_id=1).read_from_s3(file_path=file_path)
# # print(response)
# # print(response['Body'].read().decode('utf-8'))
# from superagi.tools.file.read_file import ReadFileTool
#
# tool = ReadFileTool(agent_id=1, agent_execution_id=1,
#                     resource_manager=FileManager(session=session, agent_id=1, agent_execution_id=1))
# tool._execute(file_name='Village_Story.txt')
