from app import ma
from app.models import Submission
from marshmallow import fields, validate

class SubmissionSchema(ma.SQLAlchemyAutoSchema):
    """Schema for Submission model"""
    class Meta:
        model = Submission
        load_instance = True
        
    # Add validation
    subject = fields.String(required=True, validate=validate.Length(min=1, max=200))
    context = fields.String(required=True, validate=validate.Length(min=1))
    created_at = fields.DateTime(dump_only=True)
    
# Initialize schemas
submission_schema = SubmissionSchema()
submissions_schema = SubmissionSchema(many=True) 