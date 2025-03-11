from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, flash, jsonify, current_app
)
from flask_restx import Api, Resource, fields, reqparse
from app.models import Submission
from app.schemas import submission_schema, submissions_schema
from app.file_storage import (
    add_submission as add_submission_to_storage,
    get_submissions as get_submissions_from_storage,
    get_submission_by_id as get_submission_from_storage,
    delete_submission as delete_submission_from_storage
)
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
    
    try:
        # Print debug info
        print("=== STORAGE DEBUGGING INFO ===")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Instance path exists: {os.path.exists('instance')}")
        if os.path.exists('instance'):
            print(f"Instance path permissions: {os.stat('instance').st_mode}")
        
        # Add submission to storage
        submission_data = add_submission_to_storage(subject, context)
        
        if submission_data:
            flash('Your submission has been recorded!', 'success')
        else:
            flash('Error saving submission, please try again.', 'error')
            
    except Exception as e:
        import traceback
        print(f"Storage error: {str(e)}")
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
        submissions = get_submissions_from_storage()
        return {
            'success': True,
            'data': submissions
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
            data = request.json
            errors = submission_schema.validate(data)
            if errors:
                return {
                    'success': False,
                    'message': f'Validation error: {errors}'
                }, 400
            
            # Create new submission
            submission_data = add_submission_to_storage(
                subject=data.get('subject'),
                context=data.get('context')
            )
            
            if not submission_data:
                return {
                    'success': False,
                    'message': 'Failed to create submission'
                }, 500
            
            return {
                'success': True,
                'message': 'Submission created successfully',
                'data': submission_data
            }, 201
            
        except Exception as e:
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
        submission = get_submission_from_storage(id)
        if not submission:
            return {'success': False, 'message': 'Submission not found'}, 404
            
        return {
            'success': True,
            'data': submission
        }
    
    @ns.doc('delete_submission')
    @ns.response(204, 'Submission deleted')
    def delete(self, id):
        """Delete a submission"""
        success = delete_submission_from_storage(id)
        
        if not success:
            return {'success': False, 'message': 'Submission not found'}, 404
            
        return '', 204 