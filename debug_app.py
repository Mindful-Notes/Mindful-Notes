import sys
import os
import traceback

sys.path.append(os.getcwd())

def main():
    try:
        from app.main import app
        print("Import app.main successful")
    except Exception:
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())

if __name__ == "__main__":
    main()
