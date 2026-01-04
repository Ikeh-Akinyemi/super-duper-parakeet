"""
User file processing module with comprehensive error handling.

This module provides robust file processing capabilities with detailed
error tracking, validation, and recovery mechanisms.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Configure logging with detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FileProcessingError(Exception):
    """Custom exception for file processing errors."""
    
    def __init__(self, file_path: str, message: str, original_error: Optional[Exception] = None):
        """
        Initialize FileProcessingError.
        
        Args:
            file_path: Path to the file that caused the error
            message: Human-readable error message
            original_error: The original exception that was caught
        """
        self.file_path = file_path
        self.message = message
        self.original_error = original_error
        super().__init__(f"{message} (file: {file_path})")


def validate_file_path(file_path: str) -> bool:
    """
    Validate that a file path exists and is readable.
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if file exists and is readable, False otherwise
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception as e:
        logger.error(f"Error validating path {file_path}: {e}")
        return False


def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Safely load and parse a JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data as dictionary, or None if loading fails
        
    Raises:
        FileProcessingError: If file cannot be read or parsed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            raise FileProcessingError(
                file_path,
                "File does not contain a JSON object",
                None
            )
            
        return data
        
    except FileNotFoundError as e:
        logger.warning(f"File not found: {file_path}")
        raise FileProcessingError(
            file_path,
            "File not found",
            e
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise FileProcessingError(
            file_path,
            f"Invalid JSON format: {str(e)}",
            e
        )
        
    except PermissionError as e:
        logger.error(f"Permission denied reading {file_path}: {e}")
        raise FileProcessingError(
            file_path,
            "Permission denied",
            e
        )
        
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error in {file_path}: {e}")
        raise FileProcessingError(
            file_path,
            "File encoding error",
            e
        )
        
    except Exception as e:
        logger.error(f"Unexpected error loading {file_path}: {e}")
        raise FileProcessingError(
            file_path,
            f"Unexpected error: {str(e)}",
            e
        )


def extract_user_data(data: Dict[str, Any], file_path: str) -> Dict[str, Any]:
    """
    Extract and validate user data from parsed JSON.
    
    Args:
        data: Parsed JSON data
        file_path: Original file path (for error reporting)
        
    Returns:
        Dictionary with extracted user statistics
        
    Raises:
        FileProcessingError: If data structure is invalid
    """
    try:
        if 'users' not in data:
            logger.warning(f"No 'users' key in {file_path}, using empty list")
            users = []
        else:
            users = data['users']
            
        if not isinstance(users, list):
            raise FileProcessingError(
                file_path,
                "'users' field must be a list",
                None
            )
        
        # Calculate total value with error handling for individual users
        total_value = 0
        for idx, user in enumerate(users):
            if not isinstance(user, dict):
                logger.warning(
                    f"Invalid user entry at index {idx} in {file_path}: not a dict"
                )
                continue
                
            value = user.get('value', 0)
            
            # Ensure value is numeric
            try:
                total_value += float(value)
            except (TypeError, ValueError) as e:
                logger.warning(
                    f"Invalid value for user at index {idx} in {file_path}: {e}"
                )
                continue
        
        return {
            'file': file_path,
            'user_count': len(users),
            'total_value': total_value
        }
        
    except FileProcessingError:
        # Re-raise our custom errors
        raise
        
    except Exception as e:
        logger.error(f"Error extracting user data from {file_path}: {e}")
        raise FileProcessingError(
            file_path,
            f"Data extraction error: {str(e)}",
            e
        )


def process_user_files(file_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Process multiple user data files and return aggregated results.
    
    This function processes each file independently and continues even if
    individual files fail. Errors are logged but do not stop processing
    of remaining files.
    
    Args:
        file_paths: List of file paths to process
        
    Returns:
        List of dictionaries containing processing results for successful files
        
    Raises:
        ValueError: If file_paths is not a list or is empty
    """
    # Validate input
    if not isinstance(file_paths, list):
        raise ValueError("file_paths must be a list")
    
    if not file_paths:
        logger.warning("Empty file_paths list provided")
        return []
    
    results = []
    errors = []
    
    logger.info(f"Processing {len(file_paths)} files")
    
    for path in file_paths:
        try:
            # Validate path type
            if not isinstance(path, str):
                logger.error(f"Invalid path type: {type(path)}")
                errors.append({
                    'file': str(path),
                    'error': 'Invalid path type'
                })
                continue
            
            # Pre-validate file exists
            if not validate_file_path(path):
                logger.warning(f"Skipping invalid or inaccessible path: {path}")
                errors.append({
                    'file': path,
                    'error': 'File does not exist or is not accessible'
                })
                continue
            
            # Load and parse JSON
            data = load_json_file(path)
            
            if data is None:
                errors.append({
                    'file': path,
                    'error': 'Failed to load file'
                })
                continue
            
            # Extract user data
            result = extract_user_data(data, path)
            results.append(result)
            
            logger.info(
                f"Successfully processed {path}: "
                f"{result['user_count']} users, "
                f"total value {result['total_value']}"
            )
            
        except FileProcessingError as e:
            # Our custom errors - already logged
            errors.append({
                'file': e.file_path,
                'error': e.message
            })
            
        except Exception as e:
            # Catch any unexpected errors
            logger.error(f"Unexpected error processing {path}: {e}", exc_info=True)
            errors.append({
                'file': path,
                'error': f"Unexpected error: {str(e)}"
            })
    
    # Log summary
    success_count = len(results)
    error_count = len(errors)
    
    logger.info(
        f"Processing complete: {success_count} succeeded, {error_count} failed"
    )
    
    if errors:
        logger.warning(f"Errors encountered: {errors}")
    
    return results