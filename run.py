import os
import sys

# Add the current directory to Python path
sys.path.append(os.getcwd())

# Import the Reflex app
from OracleDelphi import app

if __name__ == "__main__":
    app.run()
