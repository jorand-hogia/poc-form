from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, flash, jsonify, current_app
)
from flask_restx import Api, Resource, fields, reqparse
from app import db
from app.models import Submission
from app.schemas import submission_schema, submissions_schema
import os
import logging

# Blueprint for web interface
main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    """Home page with form"""
    return render_template('index.html')

@main_bp.route('/submit', methods=['POST'])
def submit():
    """Handle form submission"""
    subject = request.form.get('subject')
    context = request.form.get('context')
    
    # Validate input
    if not subject or not context:
        flash('Both subject and context are required!', 'error')
        return redirect(url_for('main.index'))
    
    # Create new submission
    new_submission = Submission(subject=subject, context=context)
    
    try:
        # Print debug info for SQLite
        import sqlite3
        from sqlalchemy import inspect
        from flask import current_app
        
        print("=== DATABASE DEBUGGING INFO ===")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Instance path exists: {os.path.exists('instance')}")
        if os.path.exists('instance'):
            print(f"Instance path permissions: {os.stat('instance').st_mode}")
        
        # Get database URI from config
        db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Database URI: {db_uri}")
        
        # For SQLite specifically
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            print(f"Database file path: {db_path}")
            print(f"Database file exists: {os.path.exists(db_path)}")
            if os.path.exists(db_path):
                print(f"Database file permissions: {os.stat(db_path).st_mode}")
                
                # Check if database is actually accessible
                try:
                    test_conn = sqlite3.connect(db_path)
                    test_conn.execute("SELECT 1")
                    test_conn.close()
                    print("Direct SQLite connection test: SUCCESSFUL")
                except Exception as sqlite_err:
                    print(f"Direct SQLite connection test FAILED: {str(sqlite_err)}")
        
        # Get SQLAlchemy engine and connection info
        try:
            engine = inspect(db.engine).engine
            print(f"SQLAlchemy Engine: {engine}")
            print(f"SQLAlchemy URL: {engine.url}")
        except Exception as engine_err:
            print(f"Error inspecting SQLAlchemy engine: {str(engine_err)}")
        
        # Ensure instance directory exists and is writable
        if not os.path.exists('instance'):
            os.makedirs('instance', exist_ok=True)
            print(f"Created instance directory")
        os.chmod('instance', 0o777)  # Full permissions
        print(f"Set permissions on instance directory")
            
        # Try to force creation of database if it doesn't exist
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created database directory: {db_dir}")
            
            if not os.path.exists(db_path):
                # Create empty database file
                with open(db_path, 'w') as f:
                    pass
                os.chmod(db_path, 0o666)  # Read/write permissions
                print(f"Created empty database file: {db_path}")
                
                # Initialize schema
                with current_app.app_context():
                    db.create_all()
                    print("Created database schema")
        
        # Add to database with extra error handling
        db.session.add(new_submission)
        db.session.commit()
        flash('Your submission has been recorded!', 'success')
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Database error: {str(e)}")
        print(traceback.format_exc())
        
        # Try to recover and create database
        try:
            with current_app.app_context():
                db.create_all()
                print("Attempted database recovery by creating schema")
                
                # Try again to save
                db.session.add(new_submission)
                db.session.commit()
                flash('Your submission has been recorded after recovery!', 'success')
                print("Recovery successful!")
                return redirect(url_for('main.index'))
        except Exception as recovery_err:
            print(f"Recovery failed: {str(recovery_err)}")
            flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))

# Blueprint for API with RESTx
api_bp = Blueprint('api', __name__)
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Api(
    api_bp,
    version='1.0',
    title='Form Submissions API',
    description='API for managing form submissions',
    doc='/docs',
    authorizations=authorizations,
    prefix='/api'
)

# Create namespace
ns = api.namespace('submissions', description='Submission operations')

# Define models
submission_model = api.model('Submission', {
    'subject': fields.String(required=True, description='Subject of the submission', max_length=200),
    'context': fields.String(required=True, description='Context of the submission')
})

submission_response = api.model('SubmissionResponse', {
    'id': fields.Integer(description='The unique identifier'),
    'subject': fields.String(description='The subject of the submission'),
    'context': fields.String(description='The context of the submission'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

list_response = api.model('SubmissionListResponse', {
    'success': fields.Boolean(description='Operation status'),
    'data': fields.List(fields.Nested(submission_response), description='List of submissions')
})

create_response = api.model('SubmissionCreateResponse', {
    'success': fields.Boolean(description='Operation status'),
    'message': fields.String(description='Status message'),
    'data': fields.Nested(submission_response, description='Created submission')
})

@ns.route('')
class SubmissionList(Resource):
    @ns.doc('list_submissions')
    @ns.response(200, 'Success', list_response)
    def get(self):
        """List all submissions"""
        submissions = Submission.query.order_by(Submission.created_at.desc()).all()
        return {
            'success': True,
            'data': submissions_schema.dump(submissions)
        }
    
    @ns.doc('create_submission')
    @ns.expect(submission_model)
    @ns.response(201, 'Submission created', create_response)
    @ns.response(400, 'Validation error')
    @ns.response(500, 'Server error')
    def post(self):
        """Create a new submission"""
        try:
            # Validate and deserialize input
            data = submission_schema.load(request.json)
            
            # Create new submission
            db.session.add(data)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Submission created successfully',
                'data': submission_schema.dump(data)
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': str(e)
            }, 500

@ns.route('/<int:id>')
@ns.param('id', 'The submission identifier')
@ns.response(404, 'Submission not found')
class SubmissionItem(Resource):
    @ns.doc('get_submission')
    @ns.response(200, 'Success', create_response)
    def get(self, id):
        """Get a specific submission"""
        submission = Submission.query.get_or_404(id)
        return {
            'success': True,
            'data': submission_schema.dump(submission)
        }
    
    @ns.doc('delete_submission')
    @ns.response(204, 'Submission deleted')
    def delete(self, id):
        """Delete a submission"""
        submission = Submission.query.get_or_404(id)
        db.session.delete(submission)
        db.session.commit()
        return '', 204 