from app import create_app
from app.models import Submission

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'Submission': Submission}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 