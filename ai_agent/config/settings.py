"""
Configuration management for AI Sales Intelligence Agent
Builds on existing config.py patterns from the main project
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


class AIAgentConfig:
    """Configuration class for AI Sales Intelligence Agent"""

    def __init__(self):
        """Initialize configuration with validation"""
        self.groq_api_key = self._get_groq_api_key()
        self.model_name = self._get_model_name()
        self.chunk_size = self._get_chunk_size()
        self.timeout_seconds = self._get_timeout()
        self.max_retries = self._get_max_retries()
        self.concurrent_requests = self._get_concurrent_requests()

    def _get_groq_api_key(self) -> str:
        """Get Groq API key from environment with detailed error messages"""
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ConfigurationError(
                "GROQ_API_KEY not found in environment variables.\n"
                "To fix this:\n"
                f"1. Add GROQ_API_KEY=your_key_here to {env_path}\n"
                "2. Or set environment variable: export GROQ_API_KEY=your_key_here\n"
                "3. Get your API key from: https://console.groq.com/keys"
            )

        # Basic validation
        if len(api_key.strip()) < 10:
            raise ConfigurationError(
                "GROQ_API_KEY appears to be invalid (too short).\n"
                "Please check your API key from https://console.groq.com/keys"
            )

        return api_key.strip()

    def _get_model_name(self) -> str:
        """Get model name with validated fallback"""
        model = os.getenv('GROQ_MODEL_NAME', 'meta-llama/llama-4-scout-17b-16e-instruct')
        if not model:
            raise ConfigurationError("Model name cannot be empty")
        return model

    def _get_chunk_size(self) -> int:
        """Get processing chunk size with validation"""
        try:
            chunk_size = int(os.getenv('CHUNK_SIZE', '200'))
            if chunk_size <= 0:
                raise ConfigurationError("CHUNK_SIZE must be a positive integer")
            if chunk_size > 1000:
                raise ConfigurationError("CHUNK_SIZE too large (max 1000), use smaller chunks")
            return chunk_size
        except ValueError:
            raise ConfigurationError("CHUNK_SIZE must be a valid integer")

    def _get_timeout(self) -> int:
        """Get timeout for operations in seconds with validation"""
        try:
            timeout = int(os.getenv('TIMEOUT_SECONDS', '15'))
            if timeout <= 0:
                raise ConfigurationError("TIMEOUT_SECONDS must be a positive integer")
            if timeout > 300:
                raise ConfigurationError("TIMEOUT_SECONDS too large (max 300 seconds)")
            return timeout
        except ValueError:
            raise ConfigurationError("TIMEOUT_SECONDS must be a valid integer")

    def _get_max_retries(self) -> int:
        """Get maximum retries with validation"""
        try:
            retries = int(os.getenv('MAX_RETRIES', '3'))
            if retries < 0:
                raise ConfigurationError("MAX_RETRIES must be non-negative")
            if retries > 10:
                raise ConfigurationError("MAX_RETRIES too large (max 10)")
            return retries
        except ValueError:
            raise ConfigurationError("MAX_RETRIES must be a valid integer")

    def _get_concurrent_requests(self) -> int:
        """Get concurrent request limit with validation"""
        try:
            concurrent = int(os.getenv('CONCURRENT_REQUESTS', '5'))
            if concurrent <= 0:
                raise ConfigurationError("CONCURRENT_REQUESTS must be positive")
            if concurrent > 20:
                raise ConfigurationError("CONCURRENT_REQUESTS too large (max 20)")
            return concurrent
        except ValueError:
            raise ConfigurationError("CONCURRENT_REQUESTS must be a valid integer")

    def validate(self) -> bool:
        """Validate complete configuration"""
        try:
            # All validation is done in getters, so if we got here, we're valid
            assert self.groq_api_key, "API key validation failed"
            assert self.model_name, "Model name validation failed"
            assert self.chunk_size > 0, "Chunk size validation failed"
            assert self.timeout_seconds > 0, "Timeout validation failed"
            assert self.max_retries >= 0, "Max retries validation failed"
            assert self.concurrent_requests > 0, "Concurrent requests validation failed"
            return True
        except AssertionError as e:
            raise ConfigurationError(f"Configuration validation failed: {e}")

    def display_config(self, mask_secrets: bool = True) -> Dict[str, Any]:
        """Display current configuration (with masked secrets)"""
        api_key_display = f"{self.groq_api_key[:8]}..." if mask_secrets else self.groq_api_key

        return {
            "groq_api_key": api_key_display,
            "model_name": self.model_name,
            "chunk_size": self.chunk_size,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "concurrent_requests": self.concurrent_requests,
            "env_file_path": str(env_path),
            "env_file_exists": env_path.exists()
        }

    def test_groq_connection(self) -> bool:
        """Test Groq API connection (placeholder for actual implementation)"""
        # This will be implemented when we add the Groq client
        # For now, just validate the API key format
        return len(self.groq_api_key) > 10 and self.groq_api_key.startswith('gsk_')


# Global configuration instance (created on-demand)
def get_config() -> AIAgentConfig:
    """Get or create global configuration instance"""
    return AIAgentConfig()


# Create default config instance for backward compatibility
# This will be created when first accessed in main.py
config = None
