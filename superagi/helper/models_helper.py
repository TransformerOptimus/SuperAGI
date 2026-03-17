import ipaddress
import socket
from superagi.llms.hugging_face import HuggingFace
from urllib.parse import urlparse


def is_safe_url(url: str) -> bool:
    """
    Check if a URL is safe for outbound requests.

    Prevents SSRF by allowing only HTTP/HTTPS URLs and blocking
    localhost, private, and internal IP addresses.

    Args:
        url (str): URL to validate.

    Returns:
        bool: True if safe, False otherwise.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        # Block localhost
        if hostname in ["localhost", "127.0.0.1"]:
            return False
        # Resolve IP
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        # Block internal/private IPs
        if (
            ip_obj.is_private or
            ip_obj.is_loopback or
            ip_obj.is_reserved or
            ip_obj.is_link_local
        ):
            return False

        return True

    except Exception:
        return False


class ModelsHelper:
    @staticmethod
    def validate_end_point(model_api_key, end_point, model_provider):
        response = {"success": True}

        if not end_point or not is_safe_url(end_point):
            response['success'] = False
            response['error'] = "Invalid or unsafe endpoint URL"
            try:
                return response
            except Exception:
                return {"message": response.text}

        if (model_provider == 'Hugging Face'):
            try:
                result = HuggingFace(api_key=model_api_key, end_point=end_point).verify_end_point()
            except Exception as e:
                response['success'] = False
                response['error'] = str(e)
            else:
                response['result'] = result

        return response