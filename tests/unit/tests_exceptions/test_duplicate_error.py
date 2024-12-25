import pytest

from app.exceptions.duplicate_error import DuplicateError  # Corrected import path

def test_duplicate_error_initialization():
    """Test that the DuplicateError is initialized correctly."""
    message = "This is a test duplicate error message."
    error = DuplicateError(message)
    assert error.message == message, "The error message should be correctly initialized."

def test_duplicate_error_string_representation():
    """Test the string representation of the DuplicateError."""
    message = "Another test duplicate error message."
    error = DuplicateError(message)
    assert str(error) == message, "The string representation should return the message."

def test_duplicate_error_with_empty_message():
    """Test DuplicateError with an empty message."""
    message = ""
    error = DuplicateError(message)
    assert error.message == message, "The error message should be correctly initialized even if it's empty."
    assert str(error) == message, "The string representation should return the empty message."

def test_duplicate_error_with_special_characters():
    """Test DuplicateError with a message containing special characters."""
    message = "Test with special characters: !@#$%^&*()"
    error = DuplicateError(message)
    assert error.message == message, "The error message should handle special characters correctly."
    assert str(error) == message, "The string representation should return the message with special characters."

def test_duplicate_error_with_long_message():
    """Test DuplicateError with a very long message."""
    message = "This is a very long message " * 20  # Repeat 20 times to make it long
    error = DuplicateError(message)
    assert error.message == message, "The error message should handle long messages correctly."
    assert str(error) == message, "The string representation should return the long message."