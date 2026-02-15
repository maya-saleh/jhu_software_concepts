import os
import sys

# Add module_4/ so "import src..." works
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # module_4/

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
