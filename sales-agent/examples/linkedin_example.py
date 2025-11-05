"""
LinkedIn Tool Usage Examples

Demonstrates how to use LinkedIn tools for multi-channel outreach
"""

import sys
sys.path.append('..')

from tools.linkedin.connection_tool import LinkedInConnectionTool
from tools.linkedin.message_tool import LinkedInMessageTool
from tools.linkedin.visit_tool import LinkedInProfileVisitTool
from tools.linkedin.search_tool import LinkedInSearchTool
from tools.linkedin.response_tool import LinkedInResponseTool
from tools.linkedin.rate_limiter import LinkedInRateLimiter
import time


def example_1_send_connection_request():
    """Example 1: Send a personalized connection request"""
    print("\n" + "="*60)
    print("Example 1: Send Connection Request")
    print("="*60)

    tool = LinkedInConnectionTool(provider="phantombuster")

    result = tool.execute(
        profile_url="https://www.linkedin.com/in/example-profile",
        message="""Hi John,

I saw your post about scaling sales operations at TechCorp. We're helping
similar companies increase pipeline efficiency by 3x.

Would love to connect and share some insights!""",
        include_note=True
    )

    print(f"\nResult: {result}")


def example_2_search_and_connect():
    """Example 2: Search for prospects and send connections"""
    print("\n" + "="*60)
    print("Example 2: Search & Connect Workflow")
    print("="*60)

    # Search for prospects
    search_tool = LinkedInSearchTool(provider="phantombuster")

    print("\n1. Searching for prospects...")
    prospects = search_tool.execute(
        title="VP of Sales",
        location="San Francisco Bay Area",
        limit=5
    )

    print(f"Found {len(prospects)} prospects")

    # Send connection requests
    connection_tool = LinkedInConnectionTool(provider="phantombuster")

    for i, prospect in enumerate(prospects[:3], 1):  # Limit to 3 for demo
        print(f"\n2. Connecting with {prospect.get('name')}...")

        # Personalized message
        message = f"""Hi {prospect.get('name', '').split()[0]},

I noticed you're working as {prospect.get('title')} at {prospect.get('company')}.
We're helping companies like yours accelerate sales growth through automation.

Would love to connect!"""

        result = connection_tool.execute(
            profile_url=prospect.get('profile_url'),
            message=message,
            include_note=True
        )

        print(f"Result: {result.get('message')}")

        # Wait between requests (safety)
        if i < 3:
            print("Waiting 2 minutes for safety...")
            time.sleep(120)


def example_3_visit_then_connect():
    """Example 3: Visit profile, then connect (warm outreach)"""
    print("\n" + "="*60)
    print("Example 3: Warm Outreach (Visit → Connect)")
    print("="*60)

    profile_url = "https://www.linkedin.com/in/example-profile"

    # Step 1: Visit profile
    print("\n1. Visiting profile...")
    visit_tool = LinkedInProfileVisitTool(provider="phantombuster")
    visit_result = visit_tool.execute(profile_url=profile_url)
    print(f"Visit result: {visit_result.get('message')}")

    # Step 2: Wait 24 hours (simulated)
    print("\n2. Waiting 24 hours (simulated - skipping for demo)")
    # time.sleep(86400)  # Uncomment for real usage

    # Step 3: Send connection
    print("\n3. Sending connection request...")
    connection_tool = LinkedInConnectionTool(provider="phantombuster")
    connection_result = connection_tool.execute(
        profile_url=profile_url,
        message="Hi! I noticed you viewed my profile. Would love to connect!",
        include_note=True
    )
    print(f"Connection result: {connection_result.get('message')}")


def example_4_multi_channel_sequence():
    """Example 4: Multi-channel sequence (LinkedIn + Email)"""
    print("\n" + "="*60)
    print("Example 4: Multi-Channel Sequence")
    print("="*60)

    # Lead data
    lead = {
        "name": "John Smith",
        "email": "john@company.com",
        "linkedin_url": "https://www.linkedin.com/in/johnsmith",
        "company": "TechCorp",
        "title": "VP of Sales"
    }

    print(f"\nExecuting sequence for {lead['name']}...")

    # Day 1: LinkedIn visit
    print("\n[Day 1] Visiting LinkedIn profile...")
    visit_tool = LinkedInProfileVisitTool(provider="phantombuster")
    visit_tool.execute(profile_url=lead['linkedin_url'])

    # Day 2: Email outreach
    print("\n[Day 2] Sending email...")
    # email_tool.execute(to=lead['email'], subject="...", body="...")
    print("Email sent (simulated)")

    # Day 3: LinkedIn connection
    print("\n[Day 3] Sending LinkedIn connection...")
    connection_tool = LinkedInConnectionTool(provider="phantombuster")
    connection_tool.execute(
        profile_url=lead['linkedin_url'],
        message=f"Hi {lead['name'].split()[0]}, following up on my email. Let's connect!",
        include_note=True
    )

    # Day 7: LinkedIn message (if connected)
    print("\n[Day 7] Sending LinkedIn message (if connected)...")
    message_tool = LinkedInMessageTool(provider="phantombuster")
    message_tool.execute(
        profile_url=lead['linkedin_url'],
        message=f"""Hi {lead['name'].split()[0]},

Thanks for connecting! Did you get a chance to review my email about
how we're helping companies like {lead['company']} scale sales operations?

Happy to jump on a quick call this week if you're interested.

Best,
Sarah""",
        is_inmail=False
    )


def example_5_check_responses():
    """Example 5: Check for responses and new connections"""
    print("\n" + "="*60)
    print("Example 5: Check Responses")
    print("="*60)

    response_tool = LinkedInResponseTool(provider="phantombuster")

    print("\nChecking for responses from last 24 hours...")
    responses = response_tool.execute(since_hours=24)

    if responses.get('error'):
        print(f"Error: {responses['error']}")
    else:
        print(f"\n📊 Response Summary:")
        print(f"  New connections: {responses.get('total_new_connections', 0)}")
        print(f"  New messages: {responses.get('total_new_messages', 0)}")
        print(f"  Pending requests: {responses.get('total_pending', 0)}")

        # Show details
        if responses.get('new_connections'):
            print("\n✅ New Connections:")
            for conn in responses['new_connections'][:5]:
                print(f"  - {conn.get('name')} at {conn.get('company')}")


def example_6_rate_limiter():
    """Example 6: Using rate limiter"""
    print("\n" + "="*60)
    print("Example 6: Rate Limiter & Safety")
    print("="*60)

    limiter = LinkedInRateLimiter()

    # Check if we can perform actions
    print("\n1. Checking rate limits...")

    actions = ["connection_request", "message", "profile_visit"]

    for action in actions:
        can_perform, reason = limiter.can_perform_action(action)

        if can_perform:
            print(f"  ✅ {action}: Can perform")
        else:
            print(f"  ❌ {action}: {reason}")

    # Get usage stats
    print("\n2. Current usage stats:")
    stats = limiter.get_stats()

    for action_type, data in stats.items():
        print(f"\n  {action_type}:")
        print(f"    Last hour: {data['last_hour']}/{data['limits'].get('per_hour', 'N/A')}")
        print(f"    Last day: {data['last_day']}/{data['limits'].get('per_day', 'N/A')}")
        print(f"    Last week: {data['last_week']}/{data['limits'].get('per_week', 'N/A')}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("LinkedIn Tool Examples")
    print("="*60)
    print("\nNOTE: These examples require PhantomBuster configuration.")
    print("See LINKEDIN_IMPLEMENTATION_GUIDE.md for setup instructions.")
    print("\nPress Ctrl+C to stop at any time.\n")

    examples = [
        ("Send Connection Request", example_1_send_connection_request),
        ("Search & Connect", example_2_search_and_connect),
        ("Warm Outreach", example_3_visit_then_connect),
        ("Multi-Channel Sequence", example_4_multi_channel_sequence),
        ("Check Responses", example_5_check_responses),
        ("Rate Limiter", example_6_rate_limiter)
    ]

    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{'='*60}")
        print(f"Running Example {i}: {name}")
        print(f"{'='*60}\n")

        try:
            # Uncomment to run actual examples
            # func()
            print(f"Example {i} ready (uncomment func() to run)")

        except KeyboardInterrupt:
            print("\n\nStopped by user.")
            break
        except Exception as e:
            print(f"\nError in example {i}: {str(e)}")

        if i < len(examples):
            input("\nPress Enter to continue to next example...")


if __name__ == "__main__":
    # Show menu
    print("\nLinkedIn Tool Examples")
    print("="*60)
    print("1. Send Connection Request")
    print("2. Search & Connect Workflow")
    print("3. Warm Outreach (Visit → Connect)")
    print("4. Multi-Channel Sequence")
    print("5. Check Responses")
    print("6. Rate Limiter & Safety")
    print("7. Run All Examples")
    print("="*60)

    choice = input("\nSelect example (1-7): ").strip()

    examples_map = {
        "1": example_1_send_connection_request,
        "2": example_2_search_and_connect,
        "3": example_3_visit_then_connect,
        "4": example_4_multi_channel_sequence,
        "5": example_5_check_responses,
        "6": example_6_rate_limiter,
        "7": main
    }

    func = examples_map.get(choice)

    if func:
        func()
    else:
        print("\nInvalid choice. Run 'python linkedin_example.py' again.")
