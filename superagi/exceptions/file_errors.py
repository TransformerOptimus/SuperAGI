
class UnsupportedFileTypeError(Exception):
    def __init__(self, file_name: str, supported_types: list):
        message = f"Unsupported file type for '{file_name}'. Supported types are: {', '.join(supported_types)}"
        super().__init__(message)

class FileNotCreatedError(Exception):
    def __init__(self, file_name: str):
        message = f"Failed to create the file '{file_name}'."
        super().__init__(message)