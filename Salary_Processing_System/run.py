"""
PayCore Enterprise — Launch Script
Run this file to start the application:
    python run.py
"""
import sys
import os

# Add paycore package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "paycore"))

from main import main

if __name__ == "__main__":
    main()
