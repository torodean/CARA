#!/bin/python3
"""
 conftest.py
 Created by: Antonius Torode
 Description: Pytest configuration for the CARA test suite. Adds the directory
 containing cara.py to the import path so the tests can be run with pytest
 from any working directory (previously relied on a relative '../' append
 that only worked when pytest was launched from inside the test directory).
"""
import os
import sys

# Insert the parent directory (bin/), which contains cara.py, at the front
# of the import path. The path is derived from this file's location so it
# resolves correctly no matter where pytest is launched from.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
