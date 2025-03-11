from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import os
from flask_cors import CORS
from flask_restx import Api

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

def create_app(test_config=None):
    """Application factory for Flask app"""
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///instance/submissions.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=True,  # Add SQL query logging
        # Add Swagger UI settings
        RESTX_SWAGGER_UI_DOC_EXPANSION='list',
        RESTX_VALIDATE=True,
        RESTX_MASK_SWAGGER=False,
        RESTX_ERROR_404_HELP=False,
    )

    # Debug output for database connection
    print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Instance path: {app.instance_path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Instance folder exists: {os.path.exists(app.instance_path)}")
    
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
    except Exception as e:
        print(f"Error creating instance folder: {str(e)}")
    
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