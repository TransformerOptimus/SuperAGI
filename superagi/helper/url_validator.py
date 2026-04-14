"""
URL validation helpers to mitigate Server-Side Request Forgery (SSRF).

When a URL is supplied by an untrusted source (for example, an LLM agent
driven by user input), we must not blindly issue HTTP requests to it.
Attackers can direct requests at internal services — cloud metadata
endpoints (``169.254.169.254``), loopback addresses, or RFC1918 ranges —
to exfiltrate credentials or probe internal infrastructure (CWE-918).

``validate_public_url`` enforces an allow-list of schemes and a deny-list
of internal network ranges before any outbound request is made.
"""

import ipaddress
import socket
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}

BLOCKED_HOSTNAMES = {
    "metadata.google.internal",
    "metadata.goog",
    "metadata.azure.com",
    "metadata.packet.net",
}


def _is_disallowed_ip(ip: ipaddress._BaseAddress) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def validate_public_url(url: str) -> None:
    """
    Raise ``ValueError`` if ``url`` is unsafe to fetch from a server process.

    The URL is rejected when any of the following is true:
      * the scheme is not ``http`` or ``https``
      * the hostname is missing
      * the hostname matches a known cloud-metadata host
      * the hostname resolves to a private, loopback, link-local,
        multicast, reserved, or unspecified IP address

    This check must be called before ``requests.get(url)`` or any other
    outbound request driven by untrusted input.
    """
    if not isinstance(url, str) or not url:
        raise ValueError("URL must be a non-empty string")

    parsed = urlparse(url)

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError(
            f"URL scheme '{parsed.scheme}' is not allowed; "
            f"only {sorted(ALLOWED_SCHEMES)} are permitted"
        )

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("URL must include a hostname")

    if hostname.lower() in BLOCKED_HOSTNAMES:
        raise ValueError(
            f"URL host '{hostname}' is a blocked cloud-metadata endpoint"
        )

    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve hostname '{hostname}': {exc}") from exc

    for entry in addr_info:
        ip_str = entry[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if _is_disallowed_ip(ip):
            raise ValueError(
                f"URL host '{hostname}' resolves to a disallowed address "
                f"({ip_str}); refusing to fetch"
            )
