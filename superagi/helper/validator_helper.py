import re

def validate_github_link(link: str) -> bool:
    """
    Validate a GitHub link.
    Returns True if the link is valid, False otherwise.
    """
    # Regular expression pattern to match a GitHub link
    pattern = r'^https?://(?:www\.)?github\.com/[\w\-]+/[\w\-]+$'

    # Check if the link matches the pattern
    if re.match(pattern, link):
        return True

    return False
