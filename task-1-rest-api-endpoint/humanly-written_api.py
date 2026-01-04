from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    email = data.get('email')
    name = data.get('name')
    
    if not email or not name:
        return jsonify({'error': 'email and name are required'}), 400
    
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    return jsonify({
        'id': 1,
        'email': email,
        'name': name
    }), 201

if __name__ == '__main__':
    app.run(debug=True)