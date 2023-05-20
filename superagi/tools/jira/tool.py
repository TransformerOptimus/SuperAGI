from superagi.tools.base_tool import BaseTool


class JiraTool(BaseTool):
    def __init__(self):
        super().__init__("Jira", "Helps to create Jira tickets", self.create_jira_ticket)

    def execute(self):
        print("Jira tool")
        
    def create_jira_ticket(self, name: str):
        print("hello ramram", name)
        return