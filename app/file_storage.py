"""
File-based storage module to replace SQLite database.
This module provides functions to persist and retrieve data using JSON files.
"""
import json
import os
from datetime import datetime
from pathlib import Path
import logging
from flask import current_app

# Configure logging
logger = logging.getLogger(__name__)

def get_storage_dir():
    """Get the storage directory from app config or use default"""
    return current_app.config.get('STORAGE_DIR', 'instance')

def get_submissions_file():
    """Get the path to the submissions file"""
    return os.path.join(get_storage_dir(), "submissions.json")

def ensure_storage_dir():
    """Ensure the storage directory exists"""
    storage_dir = get_storage_dir()
    os.makedirs(storage_dir, exist_ok=True)
    logger.info(f"Ensured storage directory: {storage_dir}")
    
def load_submissions():
    """Load submissions from the JSON file"""
    ensure_storage_dir()
    submissions_file = get_submissions_file()
    try:
        if os.path.exists(submissions_file):
            with open(submissions_file, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading submissions: {str(e)}")
        return []

def save_submissions(submissions):
    """Save submissions to the JSON file"""
    ensure_storage_dir()
    submissions_file = get_submissions_file()
    try:
        with open(submissions_file, 'w') as f:
            json.dump(submissions, f, indent=2, default=json_serial)
        return True
    except Exception as e:
        logger.error(f"Error saving submissions: {str(e)}")
        return False
        
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def add_submission(subject, context):
    """Add a new submission to storage"""
    submissions = load_submissions()
    
    # Generate a new ID (use the next integer or start with 1)
    new_id = 1
    if submissions:
        new_id = max(s.get('id', 0) for s in submissions) + 1
        
    new_submission = {
        'id': new_id,
        'subject': subject,
        'context': context,
        'created_at': datetime.utcnow().isoformat()
    }
    
    submissions.append(new_submission)
    success = save_submissions(submissions)
    return new_submission if success else None

def get_submissions():
    """Get all submissions, sorted by created_at in descending order"""
    submissions = load_submissions()
    return sorted(submissions, key=lambda x: x.get('created_at', ''), reverse=True)

def get_submission_by_id(submission_id):
    """Get a submission by its ID"""
    submissions = load_submissions()
    for submission in submissions:
        if submission.get('id') == submission_id:
            return submission
    return None

def delete_submission(submission_id):
    """Delete a submission by its ID"""
    submissions = load_submissions()
    initial_count = len(submissions)
    
    submissions = [s for s in submissions if s.get('id') != submission_id]
    
    if len(submissions) < initial_count:
        success = save_submissions(submissions)
        return success
    
    return False 