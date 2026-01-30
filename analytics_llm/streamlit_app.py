import sys
import os

# Add the project root to sys.path to ensure absolute imports in the frontend app work correctly
# This allows this shim file to transparently launch the actual application
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from analytics_llm.frontend.app import main

if __name__ == "__main__":
    main()
