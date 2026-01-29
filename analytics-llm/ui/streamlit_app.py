import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "analytics_llm"))
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

from app import main

main()
