from datetime import datetime
from app import db

class Submission(db.Model):
    """Model for form submissions"""
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    context = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Submission {self.id}: {self.subject}>' 