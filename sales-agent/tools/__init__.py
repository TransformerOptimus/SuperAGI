from tools.apollo.apollo_tool import ApolloTool
from tools.email.send_email_tool import SendEmailTool
from tools.email.read_email_tool import ReadEmailTool
from tools.search.google_search_tool import GoogleSearchTool

# Tool registry
AVAILABLE_TOOLS = {
    "apollo_search": ApolloTool,
    "send_email": SendEmailTool,
    "read_email": ReadEmailTool,
    "google_search": GoogleSearchTool
}

__all__ = ['AVAILABLE_TOOLS', 'ApolloTool', 'SendEmailTool', 'ReadEmailTool', 'GoogleSearchTool']
