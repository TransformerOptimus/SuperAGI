
class BaseTool:
  def __init__(self, name: str, description: str):
    self.name = name
    self.description = description


  def run(self) -> str:
    return ""