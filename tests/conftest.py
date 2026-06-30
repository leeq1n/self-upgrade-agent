"""Test configuration — loads .env for LLM integration tests."""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load .env if present
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k, v)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "llm: tests that require LLM API (skipped if not configured)")
    config.addinivalue_line("markers", "network: tests that require network access (arXiv API, S2, etc.)")
    config.addinivalue_line("markers", "slow: tests that are slow (Selenium, multi-trial, >5s)")
