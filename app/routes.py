from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, flash, jsonify
)
from flask_restx import Api, Resource, fields
from app import db
from app.models import Submission
from app.schemas import submission_schema, submissions_schema
import os

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
        # Print debug info
        print(f"Current working directory: {os.getcwd()}")
        print(f"Instance path exists: {os.path.exists('instance')}")
        print(f"Instance path permissions: {os.stat('instance').st_mode}")
        
        # Add to database
        db.session.add(new_submission)
        db.session.commit()
        flash('Your submission has been recorded!', 'success')
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Database error: {str(e)}")
        print(traceback.format_exc())
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
    title='Submission API',
    description='A simple API for managing subject/context submissions',
    doc='/docs',  # This will be accessible at /api/docs
    validate=True
)

# Define namespaces
ns = api.namespace('submissions', description='Submission operations')

# Define models for request and response
submission_model = api.model('Submission', {
    'subject': fields.String(required=True, description='The subject of the submission', min_length=1, max_length=200),
    'context': fields.String(required=True, description='The context of the submission', min_length=1)
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