"""
User API endpoint with comprehensive validation and error handling.

This module provides a REST API endpoint for creating user records with
full validation of input data including email format, name constraints,
and request structure.
"""

from flask import Flask, request, jsonify
from typing import Dict, Tuple, Any
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address string to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # RFC 5322 compliant email validation pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_name(name: str) -> Tuple[bool, str]:
    """
    Validate user name.
    
    Args:
        name: Name string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "Name must be a non-empty string"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Name must be at least 2 characters long"
    
    if len(name) > 100:
        return False, "Name must not exceed 100 characters"
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s'-]+$", name):
        return False, "Name contains invalid characters"
    
    return True, ""


def validate_user_data(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validate complete user data structure.
    
    Args:
        data: Dictionary containing user data
        
    Returns:
        Tuple of (is_valid, error_message, validated_data)
    """
    if not isinstance(data, dict):
        return False, "Request body must be a JSON object", {}
    
    # Check for required fields
    if 'email' not in data:
        return False, "Missing required field: email", {}
    
    if 'name' not in data:
        return False, "Missing required field: name", {}
    
    email = data.get('email')
    name = data.get('name')
    
    # Validate email
    if not validate_email(email):
        return False, "Invalid email format", {}
    
    # Validate name
    name_valid, name_error = validate_name(name)
    if not name_valid:
        return False, name_error, {}
    
    # Return validated and sanitized data
    validated_data = {
        'email': email.strip().lower(),
        'name': name.strip()
    }
    
    return True, "", validated_data


@app.route('/users', methods=['POST'])
def create_user() -> Tuple[Dict[str, Any], int]:
    """
    Create a new user.
    
    Expected JSON body:
        {
            "email": "user@example.com",
            "name": "John Doe"
        }
    
    Returns:
        JSON response with created user data and 201 status code on success,
        or error message with appropriate error status code on failure
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if data is None:
            logger.warning("Request received with no JSON body")
            return jsonify({
                'error': 'Request body required',
                'message': 'Expected JSON request body with user data'
            }), 400
        
        # Validate user data
        is_valid, error_message, validated_data = validate_user_data(data)
        
        if not is_valid:
            logger.warning(f"Validation failed: {error_message}")
            return jsonify({
                'error': 'Validation failed',
                'message': error_message
            }), 400
        
        # In a real application, this would save to a database
        # For now, we'll just return a mock response
        user_response = {
            'id': 1,
            'email': validated_data['email'],
            'name': validated_data['name'],
            'created_at': '2025-01-04T00:00:00Z'
        }
        
        logger.info(f"User created successfully: {validated_data['email']}")
        
        return jsonify(user_response), 201
        
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in create_user: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred processing your request'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors."""
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)