"""Unit tests for ZenScan validator module."""
import pytest
from src.validator import (
    DomainPolicy,
    EndpointResult,
    UserAgentRotator,
)


def test_user_agent_rotator():
    """Test that UserAgentRotator cycles through agents."""
    agents = ["agent1", "agent2", "agent3"]
    rotator = UserAgentRotator(agents)
    assert rotator.next() == "agent1"
    assert rotator.next() == "agent2"
    assert rotator.next() == "agent3"
    assert rotator.next() == "agent1"  # cycles


def test_user_agent_rotator_defaults():
    """Test that default agents are used when none provided."""
    rotator = UserAgentRotator()
    ua = rotator.next()
    assert ua is not None
    assert len(ua) > 0
    assert "Mozilla" in ua


def test_user_agent_rotator_empty_raises():
    """Test that empty agent list raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        UserAgentRotator([])


def test_domain_policy_allows_exact_match():
    """Test that DomainPolicy allows exact domain matches."""
    policy = DomainPolicy(["example.org"])
    assert policy.is_allowed("https://example.org/path")
    assert policy.is_allowed("https://example.org/?id=1")


def test_domain_policy_allows_subdomain():
    """Test that DomainPolicy allows subdomains."""
    policy = DomainPolicy(["example.org"])
    assert policy.is_allowed("https://api.example.org/endpoint")
    assert policy.is_allowed("https://www.example.org/")


def test_domain_policy_rejects_unrelated():
    """Test that DomainPolicy rejects unrelated domains."""
    policy = DomainPolicy(["example.org"])
    assert not policy.is_allowed("https://evil.com/path")
    assert not policy.is_allowed("https://example.org.attacker.com/")


def test_domain_policy_case_insensitive():
    """Test that DomainPolicy is case-insensitive."""
    policy = DomainPolicy(["EXAMPLE.ORG"])
    assert policy.is_allowed("https://example.org/path")
    assert policy.is_allowed("https://API.EXAMPLE.ORG/endpoint")


def test_domain_policy_empty_raises():
    """Test that empty domain list raises ValueError."""
    with pytest.raises(ValueError, match="at least one"):
        DomainPolicy([])


def test_endpoint_result():
    """Test EndpointResult dataclass."""
    result = EndpointResult(
        url="https://example.org/?id=1",
        status=200,
        parameters=["id"]
    )
    assert result.url == "https://example.org/?id=1"
    assert result.status == 200
    assert result.parameters == ["id"]
