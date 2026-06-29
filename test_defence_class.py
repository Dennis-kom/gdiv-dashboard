#!/usr/bin/env python
"""Test script to verify DefenceClass can be instantiated"""

try:
    from data.external.defence_class_data_frame import DefenceClass
    print("✓ Successfully imported DefenceClass!")
    
    # Try to instantiate it
    dc = DefenceClass()
    print("✓ Successfully instantiated DefenceClass!")
    print(f"✓ DefenceClass has google_drive attribute: {hasattr(dc, 'google_drive')}")
    print(f"✓ DefenceClass._locations: {dc._locations}")
    
except TypeError as e:
    print(f"✗ TypeError: {e}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")

