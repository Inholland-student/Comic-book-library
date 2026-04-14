"""
Entry point for Flask development server
"""
import os
from app import create_app

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # This runs the Flask development server
    # In production, use Gunicorn or another WSGI server
    app.run(host='0.0.0.0', port=5000, debug=(config_name == 'development'))
