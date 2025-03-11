from datetime import datetime
import json

class Submission:
    """Model for form submissions"""
    
    def __init__(self, subject, context, id=None, created_at=None):
        self.id = id
        self.subject = subject
        self.context = context
        self.created_at = created_at or datetime.utcnow()
    
    def __repr__(self):
        return f'<Submission {self.id}: {self.subject}>'
    
    @classmethod
    def from_dict(cls, data):
        """Create a Submission instance from a dictionary"""
        if not data:
            return None
            
        if isinstance(data.get('created_at'), str):
            # Convert ISO format string to datetime
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                created_at = datetime.utcnow()
        else:
            created_at = data.get('created_at', datetime.utcnow())
            
        return cls(
            id=data.get('id'),
            subject=data.get('subject'),
            context=data.get('context'),
            created_at=created_at
        )
    
    def to_dict(self):
        """Convert the Submission to a dictionary"""
        return {
            'id': self.id,
            'subject': self.subject,
            'context': self.context,
            'created_at': self.created_at
        } 