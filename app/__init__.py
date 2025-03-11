from flask import Flask, request, current_app
from flask_marshmallow import Marshmallow
import os
from flask_cors import CORS
from flask_restx import Api
import sys
import logging
import flask

# Initialize extensions
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
    
    # Debug output for storage
    print(f"Instance path: {app.instance_path}")
    print(f"Current directory: {os.getcwd()}")
    
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
    
    # Set up logging
    app.logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.info('Application starting up')
    
    # Initialize extensions
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
    
    # Initialize file storage
    from app.file_storage import ensure_storage_dir
    with app.app_context():
        ensure_storage_dir()
        
    return app 