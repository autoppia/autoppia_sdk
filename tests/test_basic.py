"""
Basic tests for Autoppia SDK

This file contains basic tests to verify the SDK structure and imports.
"""

import pytest
from autoppia import AutomataAgent, AutomataClient
from autoppia.src.workers import AIWorker, WorkerConfig
from autoppia.src.llms import LLMRegistry, OpenAIService


def test_imports():
    """Test that main classes can be imported."""
    assert AutomataAgent is not None
    assert AutomataClient is not None
    assert AIWorker is not None
    assert WorkerConfig is not None
    assert LLMRegistry is not None
    assert OpenAIService is not None


def test_worker_config():
    """Test WorkerConfig creation."""
    config = WorkerConfig(name="test-worker")
    assert config.name == "test-worker"
    assert config.system_prompt is None
    assert config.llms == {}


def test_llm_registry():
    """Test LLMRegistry singleton behavior."""
    registry1 = LLMRegistry()
    registry2 = LLMRegistry()
    assert registry1 is registry2


if __name__ == "__main__":
    pytest.main([__file__])
