#!/usr/bin/env python3
"""
Script to seed the database with dummy data
Run this after setting up the database
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from seed_data import seed_dummy_data

if __name__ == "__main__":
    print("Starting database seeding...")
    seed_dummy_data()
    print("Seeding completed!")
