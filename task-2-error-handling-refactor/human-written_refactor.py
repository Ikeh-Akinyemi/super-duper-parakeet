import json
import logging

logger = logging.getLogger(__name__)

def process_user_files(file_paths):
    """Process multiple user data files and return aggregated results."""
    results = []
    
    for path in file_paths:
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                results.append({
                    'file': path,
                    'user_count': len(data.get('users', [])),
                    'total_value': sum(u.get('value', 0) for u in data['users'])
                })
        except FileNotFoundError:
            logger.warning(f"File not found: {path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {path}: {e}")
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
    
    return results