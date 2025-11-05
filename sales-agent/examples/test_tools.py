"""
Test individual tools
"""

from tools.apollo.apollo_tool import ApolloTool
from tools.email.send_email_tool import SendEmailTool
from tools.search.google_search_tool import GoogleSearchTool


def test_apollo_search():
    """Test Apollo lead search"""
    print("\n=== Testing Apollo Search ===")

    apollo = ApolloTool()

    try:
        results = apollo.execute(
            person_titles=["VP of Sales", "Director of Sales"],
            per_page=5,
            num_of_employees=[50, 200],
            person_location="United States"
        )

        print(f"Found {len(results)} leads:")
        for i, lead in enumerate(results[:3], 1):
            print(f"\n{i}. {lead.get('name')}")
            print(f"   Company: {lead.get('company')}")
            print(f"   Title: {lead.get('title')}")
            print(f"   Email: {lead.get('email')}")
            print(f"   LinkedIn: {lead.get('linkedin_url')}")

    except Exception as e:
        print(f"Error: {str(e)}")


def test_google_search():
    """Test Google Search"""
    print("\n=== Testing Google Search ===")

    search = GoogleSearchTool()

    try:
        results = search.execute(
            query="Salesforce recent news 2025",
            num_results=3
        )

        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('title')}")
            print(f"   Link: {result.get('link')}")
            print(f"   Snippet: {result.get('snippet')[:100]}...")

    except Exception as e:
        print(f"Error: {str(e)}")


def test_email_tool():
    """Test Email Tool (draft mode recommended)"""
    print("\n=== Testing Email Tool ===")
    print("NOTE: Make sure EMAIL_DRAFT_MODE=FALSE in .env to actually send")

    email = SendEmailTool()

    try:
        result = email.execute(
            to="test@example.com",
            subject="Test Email from Sales Agent",
            body="""Hi there,

This is a test email from the Sales Agent system.

If you're receiving this, the email integration is working correctly!

Best regards,
Sales Agent Team"""
        )

        print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("================================")
    print("Sales Agent - Tool Testing")
    print("================================")

    # Uncomment to test each tool
    # WARNING: These will make real API calls

    # test_apollo_search()
    # test_google_search()
    # test_email_tool()

    print("\n================================")
    print("To run tests, uncomment the test")
    print("functions in the main block.")
    print("================================\n")
