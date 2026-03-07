import sys
import os

# Tambahkan src ke path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'src'))

# Update path di app/app.py sebelum exec
os.chdir(BASE_DIR)

exec(open(os.path.join(BASE_DIR, 'app', 'app.py')).read())