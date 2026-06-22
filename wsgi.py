import sys
import os

path = '/home/yourusername/wealthforge'
if path not in sys.path:
    sys.path.append(path)

os.chdir(path)

from app import app as application
