"""Server-side URL validation for vehicle data scraping sources."""

from __future__ import annotations

import ipaddress
import socket
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests


# Portfolio version: real production domains have been replaced with example
# placeholders. In production this allowlist points to 3 real, specialized
# automotive data sources.
ALLOWED_SOURCE_DOMAINS = {
    "url1": "source1.example.com",
    "url2": "source2.example.com",
    "url3": "source3.example.com",
}

BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
}

METADATA_IPS = {
    ipaddress.ip_address("169.254.169.254"),
}


class URLValidationError(ValueError):
    """Raised when a scraping URL is not safe or not allowed."""


def validate_scraping_url(url: Optional[str], source_key: str) -> Optional[str]:
    """Validate a user-provided scraping URL for the expected source.

    Returns a stripped URL when valid, or None when the input is empty.
    Raises URLValidationError when the URL is unsafe or not allowed.
    """
    if not url or not url.strip():
        return None

    candidate_url = url.strip()
    expected_domain = ALLOWED_SOURCE_DOMAINS.get(source_key)
    if not expected_domain:
        raise URLValidationError("Unknown scraping source.")

    _validate_single_url(candidate_url, expected_domain)
    _validate_redirect_chain(candidate_url, expected_domain)
    return candidate_url


def _validate_single_url(url: str, expected_domain: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme.lower() != "https":
        raise URLValidationError("Only HTTPS URLs are allowed.")

    if not parsed.hostname:
        raise URLValidationError("URL must include a valid hostname.")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in BLOCKED_HOSTNAMES:
        raise URLValidationError("Local or metadata hosts are not allowed.")

    if not _hostname_matches_allowed_domain(hostname, expected_domain):
        raise URLValidationError(f"URL host must belong to {expected_domain}.")

    _reject_unsafe_host_addresses(hostname)


def _hostname_matches_allowed_domain(hostname: str, expected_domain: str) -> bool:
    normalized_hostname = hostname[4:] if hostname.startswith("www.") else hostname
    return normalized_hostname == expected_domain or normalized_hostname.endswith(f".{expected_domain}")


def _reject_unsafe_host_addresses(hostname: str) -> None:
    ip_literal = _parse_ip_address(hostname)
    if ip_literal:
        _reject_unsafe_ip(ip_literal)
        return

    try:
        resolved_addresses = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise URLValidationError("URL hostname could not be resolved.") from exc

    for result in resolved_addresses:
        resolved_ip = ipaddress.ip_address(result[4][0])
        _reject_unsafe_ip(resolved_ip)


def _parse_ip_address(hostname: str) -> Optional[ipaddress._BaseAddress]:
    try:
        return ipaddress.ip_address(hostname)
    except ValueError:
        return None


def _reject_unsafe_ip(ip_address: ipaddress._BaseAddress) -> None:
    if (
        ip_address.is_private
        or ip_address.is_loopback
        or ip_address.is_link_local
        or ip_address.is_multicast
        or ip_address.is_reserved
        or ip_address.is_unspecified
        or ip_address in METADATA_IPS
    ):
        raise URLValidationError("Local, private, loopback, or metadata addresses are not allowed.")


def _validate_redirect_chain(url: str, expected_domain: str, max_redirects: int = 5) -> None:
    current_url = url
    session = requests.Session()
    session.trust_env = False

    for _ in range(max_redirects + 1):
        response = None
        try:
            response = session.head(current_url, allow_redirects=False, timeout=5)
            if response.status_code == 405:
                response.close()
                response = session.get(current_url, allow_redirects=False, timeout=5, stream=True)
        except requests.RequestException as exc:
            raise URLValidationError("URL could not be reached for validation.") from exc
        finally:
            if response is not None:
                response.close()

        if response is None or not response.is_redirect:
            return

        location = response.headers.get("Location")
        if not location:
            raise URLValidationError("Redirect response is missing a Location header.")

        current_url = urljoin(current_url, location)
        _validate_single_url(current_url, expected_domain)

    raise URLValidationError("URL has too many redirects.")
