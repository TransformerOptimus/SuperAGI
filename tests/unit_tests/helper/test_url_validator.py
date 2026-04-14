"""Tests for superagi.helper.url_validator (SSRF mitigation)."""

from unittest.mock import patch

import pytest

from superagi.helper.url_validator import validate_public_url


def _mock_resolve(ip: str):
    """Return a fake socket.getaddrinfo result resolving to a single IP."""
    return [(0, 0, 0, "", (ip, 0))]


class TestValidatePublicUrl:
    def test_valid_http_public_url_passes(self):
        with patch("socket.getaddrinfo", return_value=_mock_resolve("93.184.216.34")):
            validate_public_url("http://example.com/path")

    def test_valid_https_public_url_passes(self):
        with patch("socket.getaddrinfo", return_value=_mock_resolve("93.184.216.34")):
            validate_public_url("https://example.com/")

    @pytest.mark.parametrize("bad_url", ["", None, 123])
    def test_empty_or_non_string_rejected(self, bad_url):
        with pytest.raises(ValueError):
            validate_public_url(bad_url)

    @pytest.mark.parametrize(
        "url",
        [
            "ftp://example.com/file",
            "file:///etc/passwd",
            "gopher://example.com/",
            "data:text/plain,hello",
        ],
    )
    def test_disallowed_scheme_rejected(self, url):
        with pytest.raises(ValueError, match="scheme"):
            validate_public_url(url)

    def test_missing_hostname_rejected(self):
        with pytest.raises(ValueError, match="hostname"):
            validate_public_url("http:///no-host")

    def test_aws_metadata_ip_rejected(self):
        with pytest.raises(ValueError, match="disallowed"):
            validate_public_url("http://169.254.169.254/latest/meta-data/")

    def test_gcp_metadata_host_rejected(self):
        with pytest.raises(ValueError, match="metadata"):
            validate_public_url("http://metadata.google.internal/computeMetadata/v1/")

    @pytest.mark.parametrize(
        "internal_ip",
        [
            "127.0.0.1",
            "10.0.0.1",
            "172.16.0.1",
            "192.168.1.1",
            "169.254.1.1",
            "0.0.0.0",
            "::1",
            "fc00::1",
        ],
    )
    def test_internal_ip_literal_rejected(self, internal_ip):
        host = f"[{internal_ip}]" if ":" in internal_ip else internal_ip
        with pytest.raises(ValueError, match="disallowed"):
            validate_public_url(f"http://{host}/")

    def test_dns_rebind_style_hostname_rejected(self):
        """A hostname that resolves to a private IP must be blocked."""
        with patch("socket.getaddrinfo", return_value=_mock_resolve("10.0.0.5")):
            with pytest.raises(ValueError, match="disallowed"):
                validate_public_url("http://attacker-controlled.example/")

    def test_unresolvable_hostname_rejected(self):
        import socket as _socket

        with patch(
            "socket.getaddrinfo", side_effect=_socket.gaierror("nodename nor servname")
        ):
            with pytest.raises(ValueError, match="resolve"):
                validate_public_url("http://does-not-exist.invalid/")
