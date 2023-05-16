from superagi.agent.agent_prompt import AgentPrompt


class AgentPromptBuilder:
  def __init__(self, agent):
    self.agent_prompt = AgentPrompt()

  def set_base_prompt(self, base_prompt):
    self.agent_prompt.set_base_system_prompt(base_prompt)

  def add_goal(self, goal):
    self.agent_prompt.tools.append(goal)

  def add_tool(self, tool):
    self.agent_prompt.goals.append(tool)

  def add_resource(self, resource: str) -> None:
    self.agent_prompt.resources.append(resource)

  def add_constraint(self, constraint):
    self.agent_prompt.constraints.append(constraint)

  def add_evaluation(self, evaluation: str) -> None:
    self.agent_prompt.evaluations.append(evaluation)

  def set_response_format(self, response_format: str) -> None:
    self.agent_prompt.set_response_format(response_format)


  def build_agent_prompt(self):
    agent_prompt = AgentPrompt()
    prompt_start = (
      "Your decisions must always be made independently "
      "without seeking user assistance.\n"
      "Play to your strengths as an LLM and pursue simple "
      "strategies with no legal complications.\n"
      "If you have completed all your tasks, make sure to "
      'use the "finish" command.'
    )
    agent_prompt.set_base_system_prompt(prompt_start)
    agent_prompt.goals(prompt_start)

  @classmethod
  def get_autogpt_prompt(cls) -> str:
    # Initialize the PromptGenerator object
    prompt_builder = AgentPromptBuilder()
    base_prompt = (
      "Your decisions must always be made independently "
      "without seeking user assistance.\n"
      "Play to your strengths as an LLM and pursue simple "
      "strategies with no legal complications.\n"
      "If you have completed all your tasks, make sure to "
      'use the "finish" command.'
    )
    prompt_builder.set_base_prompt(base_prompt)

    # Add constraints to the PromptGenerator object
    prompt_builder.add_constraint(
        "~4000 word limit for short term memory. "
        "Your short term memory is short, "
        "so immediately save important information to files."
    )
    prompt_builder.add_constraint(
        "If you are unsure how you previously did something "
        "or want to recall past events, "
        "thinking about similar events will help you remember."
    )
    prompt_builder.add_constraint("No user assistance")
    prompt_builder.add_constraint(
        'Exclusively use the commands listed in double quotes e.g. "command name"'
    )

    # Add commands to the PromptGenerator object
    for tool in tools:
        prompt_generator.add_tool(tool)

    resources = ["Internet access for searches and information gathering.",
                 "Long Term memory management.",
                 "GPT-3.5 powered Agents for delegation of simple tasks.",
                 "File output."]
    for resource in resources:
      prompt_builder.add_resource(resource)

    # Add performance evaluations to the PromptGenerator object
    evaluations = [
        "Continuously review and analyze your actions "
        "to ensure you are performing to the best of your abilities.",
        "Constructively self-criticize your big-picture behavior constantly.",
        "Reflect on past decisions and strategies to refine your approach.",
        "Every command has a cost, so be smart and efficient. "
        "Aim to complete tasks in the least number of steps.",
    ]
    for evaluation in evaluations:
      prompt_builder.add_evaluation(evaluation)

    # Generate the prompt string
    prompt_string = prompt_generator.generate_prompt_string()

    return prompt_string