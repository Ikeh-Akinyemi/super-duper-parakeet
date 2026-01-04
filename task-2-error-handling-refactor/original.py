import json

def process_user_files(file_paths):
    """Process multiple user data files and return aggregated results."""
    results = []
    
    for path in file_paths:
        with open(path, 'r') as f:
            data = json.load(f)
            results.append({
                'file': path,
                'user_count': len(data.get('users', [])),
                'total_value': sum(u.get('value', 0) for u in data['users'])
            })
    
    return results