import sqlite3
import jwt
import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, Blueprint
from functools import wraps
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Custom metric for user actions
user_actions_total = Counter('user_actions_total', 'Total user actions', ['action', 'user'])

def get_db_connection():
    """Get SQLite connection for user authentication"""
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_postgres_connection():
    """Get PostgreSQL connection for resources table"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'postgres'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'metrics_db'),
        user=os.getenv('POSTGRES_USER', 'metrics'),
        password=os.getenv('POSTGRES_PASSWORD', 'metrics_pass')
    )

def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            request.current_user = data['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    email = data['email']
    password = data['password']
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                       (email, password)).fetchone()
    conn.close()
    
    if user:
        token = jwt.encode({
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Login successful',
            'token': token
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400

    email = data['email']
    password = data['password']

    try:
        conn = get_db_connection()
        # Check if user already exists
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if existing_user:
            conn.close()
            return jsonify({'message': 'User already exists'}), 409

        # Insert new user
        conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        conn.close()

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 500

@app.route('/verify', methods=['GET'])
@verify_token
def verify():
    return jsonify({
        'message': 'Token is valid',
        'email': request.current_user
    }), 200

# Create actions blueprint for CRUD operations
actions_bp = Blueprint('actions', __name__, url_prefix='/actions')

@actions_bp.route('/create', methods=['POST'])
@verify_token
def create_resource():
    """Create a new resource in PostgreSQL"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Missing required field: name'}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            INSERT INTO resources (name, author, annotation, kind, purpose, open_date, expiry_date, usage_conditions, url)
            VALUES (%(name)s, %(author)s, %(annotation)s, %(kind)s, %(purpose)s, %(open_date)s, %(expiry_date)s, %(usage_conditions)s, %(url)s)
            RETURNING id
        """, {
            'name': data.get('name'),
            'author': data.get('author'),
            'annotation': data.get('annotation'),
            'kind': data.get('kind'),
            'purpose': data.get('purpose'),
            'open_date': data.get('open_date'),
            'expiry_date': data.get('expiry_date'),
            'usage_conditions': data.get('usage_conditions'),
            'url': data.get('url')
        })
        
        resource_id = cursor.fetchone()['id']
        conn.commit()
        
        # Increment custom metric
        user_actions_total.labels(action='create', user=request.current_user).inc()
        
        return jsonify({
            'message': 'Resource created successfully',
            'id': resource_id
        }), 201
    except Exception:
        return jsonify({'message': 'Failed to create resource'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@actions_bp.route('/read', methods=['GET'])
@verify_token
def read_resources():
    """Read all resources from PostgreSQL"""
    conn = None
    cursor = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM resources ORDER BY created_at DESC")
        resources = cursor.fetchall()
        
        # Increment custom metric
        user_actions_total.labels(action='read', user=request.current_user).inc()
        
        return jsonify({
            'message': 'Resources retrieved successfully',
            'data': resources
        }), 200
    except Exception:
        return jsonify({'message': 'Failed to read resources'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@actions_bp.route('/update', methods=['POST'])
@verify_token
def update_resource():
    """Update a resource in PostgreSQL"""
    data = request.get_json()
    
    if not data or not data.get('id'):
        return jsonify({'message': 'Missing required field: id'}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = {'id': data['id']}
        
        for field in ['name', 'author', 'annotation', 'kind', 'purpose', 'open_date', 'expiry_date', 'usage_conditions', 'url']:
            if field in data:
                update_fields.append(f"{field} = %({field})s")
                params[field] = data[field]
        
        if not update_fields:
            return jsonify({'message': 'No fields to update'}), 400
        
        query = f"UPDATE resources SET {', '.join(update_fields)} WHERE id = %(id)s"
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            return jsonify({'message': 'Resource not found'}), 404
        
        conn.commit()
        
        # Increment custom metric
        user_actions_total.labels(action='update', user=request.current_user).inc()
        
        return jsonify({
            'message': 'Resource updated successfully',
            'id': data['id']
        }), 200
    except Exception:
        return jsonify({'message': 'Failed to update resource'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@actions_bp.route('/delete', methods=['DELETE'])
@verify_token
def delete_resource():
    """Delete a resource from PostgreSQL"""
    data = request.get_json()
    
    if not data or not data.get('id'):
        return jsonify({'message': 'Missing required field: id'}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM resources WHERE id = %s", (data['id'],))
        
        if cursor.rowcount == 0:
            return jsonify({'message': 'Resource not found'}), 404
        
        conn.commit()
        
        # Increment custom metric
        user_actions_total.labels(action='delete', user=request.current_user).inc()
        
        return jsonify({
            'message': 'Resource deleted successfully',
            'id': data['id']
        }), 200
    except Exception:
        return jsonify({'message': 'Failed to delete resource'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Register the actions blueprint
app.register_blueprint(actions_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
