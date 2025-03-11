from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import os
from flask_cors import CORS
from flask_restx import Api
import sys

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

def create_app(test_config=None):
    """Application factory for Flask app"""
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Determine if we're running in a container or locally
    in_container = os.path.exists('/.dockerenv')
    
    # Configure the app
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        # Use different paths for container vs local development
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'DATABASE_URL', 
            'sqlite:////app/instance/submissions.db' if in_container else 'sqlite:///instance/submissions.db'
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=True,  # Add SQL query logging
        # Add Swagger UI settings
        RESTX_SWAGGER_UI_DOC_EXPANSION='list',
        RESTX_VALIDATE=True,
        RESTX_MASK_SWAGGER=False,
        RESTX_ERROR_404_HELP=False,
    )

    # Enable proxy support and configure external URL handling
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['APPLICATION_ROOT'] = os.environ.get('APPLICATION_ROOT', '/')
    
    # Handle reverse proxy setup
    class ReverseProxied(object):
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            scheme = environ.get('HTTP_X_FORWARDED_PROTO')
            if scheme:
                environ['wsgi.url_scheme'] = scheme
            return self.app(environ, start_response)

    app.wsgi_app = ReverseProxied(app.wsgi_app)
    
    # Debug output for database connection
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Database URI: {db_uri}")
    print(f"Instance path: {app.instance_path}")
    print(f"Current directory: {os.getcwd()}")
    
    # For SQLite, extract the database file path and check if it's accessible
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        print(f"SQLite database file path: {db_path}")
        db_dir = os.path.dirname(db_path)
        print(f"Database directory: {db_dir}")
        print(f"Database directory exists: {os.path.exists(db_dir)}")
        print(f"Database directory is writable: {os.access(db_dir, os.W_OK)}")
        print(f"Database file exists: {os.path.exists(db_path)}")
        if os.path.exists(db_path):
            print(f"Database file permissions: {os.stat(db_path).st_mode}")
    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        print(f"Created instance folder: {app.instance_path}")
        if not os.access(app.instance_path, os.W_OK):
            print(f"WARNING: Instance path is not writable: {app.instance_path}")
            # Make it writable if possible
            try:
                os.chmod(app.instance_path, 0o777)
                print(f"Applied permissions to instance folder")
            except Exception as e:
                print(f"Could not set permissions on instance folder: {str(e)}")
    except Exception as e:
        print(f"Error with instance folder: {str(e)}")
    
    # Initialize db
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    
    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize plugins
    CORS(app)
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
        
    return app 