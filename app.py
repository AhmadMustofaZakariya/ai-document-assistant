# Root app.py - entry point untuk HuggingFace
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import semua dari app/app.py
exec(open(os.path.join(os.path.dirname(__file__), 'app', 'app.py')).read())
