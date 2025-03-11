from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import os

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
        # Add Swagger UI settings
        RESTX_SWAGGER_UI_DOC_EXPANSION='list',
        RESTX_VALIDATE=True,
        RESTX_MASK_SWAGGER=False,
        RESTX_ERROR_404_HELP=False,
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize db
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    
    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
        
    return app 