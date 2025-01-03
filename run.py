import os
import sys

# Set the PYTHONPATH to include the 'src' directory
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Import the Reflex app from the OracleDelphi module
from src.OracleDelphi.app import app

if __name__ == "__main__":
    app.run()
