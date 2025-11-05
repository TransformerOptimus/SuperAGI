"""
Example: Create a Sales Agent
"""

import requests
import json

API_URL = "http://localhost:8000/api/v1"


def create_sales_agent():
    """Create a basic sales agent"""

    agent_data = {
        "name": "Alisha - AI Sales SDR",
        "description": "AI-powered Sales Development Representative for B2B SaaS outreach",
        "goals": [
            "Find qualified leads matching our ideal customer profile",
            "Research each company thoroughly using Google Search",
            "Send highly personalized outreach emails with company-specific insights",
            "Track responses and engagement",
            "Book discovery calls with interested prospects"
        ],
        "instructions": """
You are an expert B2B sales development representative. Your process:

1. Lead Discovery: Use Apollo to find prospects matching criteria:
   - Job titles: VP of Sales, Director of Sales, Sales Manager
   - Company size: 50-500 employees
   - Location: United States

2. Research: For each lead:
   - Google search: "[Company name] recent news achievements"
   - Look for: funding rounds, product launches, expansions, challenges
   - Identify 2-3 specific insights for personalization

3. Email Composition:
   - Personalized subject line mentioning company
   - Brief intro with specific company insight
   - Value proposition relevant to their role
   - Clear CTA: "Are you available for a 15-min call this week?"
   - Keep under 150 words

4. Follow-up (if no response after 3 days):
   - Reference previous email
   - Add new value/insight
   - Soft CTA

Always be professional, concise, and respectful. Focus on providing value.
        """,
        "constraints": [
            "Only contact prospects with verified email addresses",
            "Research company before sending any email",
            "Personalize every email with company-specific insights",
            "Maximum 50 emails per day to avoid spam filters",
            "Wait at least 3 days before follow-up",
            "Never send generic template emails"
        ],
        "tools": [
            "apollo_search",
            "google_search",
            "send_email",
            "read_email"
        ],
        "model": "gpt-4",
        "max_iterations": 25,
        "iteration_interval": 300
    }

    response = requests.post(
        f"{API_URL}/agents",
        json=agent_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 201:
        agent = response.json()
        print("✓ Agent created successfully!")
        print(f"  ID: {agent['id']}")
        print(f"  Name: {agent['name']}")
        print(f"  Tools: {', '.join(agent['tools'])}")
        return agent
    else:
        print(f"✗ Failed to create agent: {response.status_code}")
        print(response.text)
        return None


def start_execution(agent_id: int):
    """Start an execution for the agent"""

    execution_data = {
        "agent_id": agent_id,
        "name": "Q4 2025 - Initial Outreach Campaign"
    }

    response = requests.post(
        f"{API_URL}/executions",
        json=execution_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 201:
        execution = response.json()
        print("\n✓ Execution started!")
        print(f"  Execution ID: {execution['id']}")
        print(f"  Status: {execution['status']}")
        print(f"  Name: {execution['name']}")
        return execution
    else:
        print(f"\n✗ Failed to start execution: {response.status_code}")
        print(response.text)
        return None


def check_status(execution_id: int):
    """Check execution status"""

    response = requests.get(f"{API_URL}/executions/{execution_id}")

    if response.status_code == 200:
        execution = response.json()
        print("\n📊 Execution Status:")
        print(f"  Status: {execution['status']}")
        print(f"  Leads Processed: {execution['leads_processed']}")
        print(f"  Emails Sent: {execution['emails_sent']}")
        print(f"  Responses: {execution['responses_received']}")
        print(f"  Current Step: {execution['current_step']}")
        return execution
    else:
        print(f"\n✗ Failed to get status: {response.status_code}")
        return None


if __name__ == "__main__":
    print("================================")
    print("Sales Agent - Example Usage")
    print("================================\n")

    # Step 1: Create agent
    print("Step 1: Creating Sales Agent...")
    agent = create_sales_agent()

    if not agent:
        exit(1)

    # Step 2: Start execution
    print("\nStep 2: Starting Execution...")
    execution = start_execution(agent['id'])

    if not execution:
        exit(1)

    # Step 3: Check status
    print("\nStep 3: Checking Status...")
    import time
    time.sleep(5)  # Wait 5 seconds
    status = check_status(execution['id'])

    print("\n================================")
    print("Next Steps:")
    print("================================")
    print(f"1. Monitor execution: GET {API_URL}/executions/{execution['id']}")
    print(f"2. View logs: GET {API_URL}/executions/{execution['id']}/logs")
    print(f"3. Check leads: GET {API_URL}/executions/{execution['id']}/leads")
    print(f"4. View stats: GET {API_URL}/stats/overview")
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("================================\n")
