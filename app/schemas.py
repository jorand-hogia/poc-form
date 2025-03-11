from app import ma
from app.models import Submission
from marshmallow import fields, validate, Schema

class SubmissionSchema(Schema):
    """Schema for Submission model"""
    id = fields.Integer(dump_only=True)
    subject = fields.String(required=True, validate=validate.Length(min=1, max=200))
    context = fields.String(required=True, validate=validate.Length(min=1))
    created_at = fields.DateTime(dump_only=True)
    
    # Custom deserializer to create Submission objects
    def make_submission(self, data, **kwargs):
        return Submission(
            subject=data.get('subject'),
            context=data.get('context')
        )
    
# Initialize schemas
submission_schema = SubmissionSchema()
submissions_schema = SubmissionSchema(many=True) 