import sys

# Add your project directory to the sys.path
project_home = '/path/to/your/project'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import your Flask app
from app import app as application
