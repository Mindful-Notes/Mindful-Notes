import sys
import os
sys.path.append(os.getcwd())

try:
    from app.main import app
    print("Import app.main successful")
except Exception as e:
    print(f"Error importing app.main: {e}")
    import traceback
    traceback.print_exc()
