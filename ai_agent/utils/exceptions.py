"""
Custom exception classes for AI Sales Intelligence Agent
"""


class AIAgentError(Exception):
    """Base exception for AI agent errors"""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


class ValidationError(AIAgentError):
    """Raised when input validation fails"""
    pass


class CSVValidationError(ValidationError):
    """Raised when CSV file validation fails"""
    pass


class URLValidationError(ValidationError):
    """Raised when URL validation fails"""
    pass


class ProcessingError(AIAgentError):
    """Raised when processing fails"""
    pass


class APIError(ProcessingError):
    """Raised when API calls fail"""
    pass


class GroqAPIError(APIError):
    """Raised when Groq API calls fail"""
    pass


class PlaywrightError(ProcessingError):
    """Raised when Playwright operations fail"""
    pass
