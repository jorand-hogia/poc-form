from app import create_app, db
from app.models import Submission

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Submission': Submission}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 