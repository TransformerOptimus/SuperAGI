import json
import pytest
import tempfile
import os
from superagi.tools.code.execute_file import ExecuteFileTool, ExecuteFileSchema
from superagi.config.config import get_config

class TestExecuteFileTool:
    def test_execute_file_success(self):
        tool = ExecuteFileTool()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False,dir=get_config('RESOURCES_INPUT_ROOT_DIR')) as tmp_file:
            tmp_file.write("print('success!')")
            tmp_file.close()
        
        args = ExecuteFileSchema(file_name=os.path.basename(tmp_file.name))
        result = tool.execute(args.file_name)
        assert result == "success!\n"
    
    def test_execute_file_error(self):
        tool = ExecuteFileTool()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False,dir=get_config('RESOURCES_OUTPUT_ROOT_DIR')) as tmp_file:
            tmp_file.write("a=1\na++\nprint(a)")
            tmp_file.close()
        
        args = ExecuteFileSchema(file_name=os.path.basename(tmp_file.name))
        result = tool.execute(args.file_name) 
        assert "Error" in result
    
    def test_execute_file_not_found(self):
        tool = ExecuteFileTool()
        args = ExecuteFileSchema(file_name="nonexistent_file.py")
        result = tool.execute(args.file_name)
        assert "not found" in result
    
    def test_execute_file_invalid_type(self):
        tool = ExecuteFileTool()
        args = ExecuteFileSchema(file_name="invalid_file.js")
        result = tool.execute(args.file_name)
        assert "Error: Invalid file type. Only python files can be executed." == result

    @classmethod
    def teardown_class(cls):
        # Clean up temporary files created during testing
        for entry in os.scandir(get_config('RESOURCES_INPUT_ROOT_DIR')):
            if entry.name.endswith(".py") and ("tmp" in entry.name):
                os.remove(entry.path)
        for entry in os.scandir(get_config('RESOURCES_OUTPUT_ROOT_DIR')):
            if entry.name.endswith(".py") and ("tmp" in entry.name):
                os.remove(entry.path)

if __name__ == "__main__":
    pytest.main(["-v", "-k", "TestExecuteFileTool"])