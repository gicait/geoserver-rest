#!/usr/bin/env python3
"""
Test script to demonstrate the absolute path fix for create_datastore function.
"""

import os
import sys
import tempfile
from geo.Geoserver import Geoserver

def test_path_conversion():
    """Test the path conversion functionality."""
    
    # Initialize GeoServer connection (adjust URL as needed)
    geo = Geoserver(
        service_url="http://localhost:8080/geoserver",
        username="admin",
        password="geoserver"
    )
    
    # Create some temporary test paths that will work on any machine
    temp_dir = tempfile.gettempdir()
    
    # Test paths using dynamic generation
    test_paths = [
        # Absolute paths (Windows-style)
        os.path.join(temp_dir, "countries.shp"),
        os.path.join(temp_dir, "data", "demo", "countries.shp"),
        
        # Absolute paths (Unix/Linux-style)
        os.path.join("/tmp", "countries.shp"),
        os.path.join("/opt", "geoserver", "data_dir", "data", "demo", "countries.shp"),
        
        # Relative paths (should remain unchanged)
        "data/demo/countries.shp",
        "countries.shp",
        
        # HTTP URLs (should remain unchanged)
        "http://localhost:8080/geoserver/wfs?request=GetCapabilities"
    ]
    
    workspace = "demo"
    
    print("Testing path conversion functionality:")
    print("=" * 50)
    
    for path in test_paths:
        print(f"\nOriginal path: {path}")
        
        # Test the path conversion logic
        if not path.startswith("http"):
            if os.path.isabs(path):
                filename = os.path.basename(path)
                relative_path = f"data/{workspace}/{filename}"
                print(f"Converted to: {relative_path}")
            else:
                print(f"Already relative: {path}")
        else:
            print("HTTP URL - no conversion needed")
    
    print("\n" + "=" * 50)
    print("Usage examples:")
    print("=" * 50)
    
    # Example 1: Using relative paths (default behavior)
    print("\n1. Using relative paths (default):")
    print("geo.create_datastore(")
    print("    name='countries',")
    print("    path='path/to/your/countries.shp',  # Your actual file path")
    print("    workspace='demo',")
    print("    use_relative_path=True  # This is the default")
    print(")")
    print("# This will create: file:data/demo/countries.shp")
    
    # Example 2: Using absolute paths (legacy behavior)
    print("\n2. Using absolute paths (legacy):")
    print("geo.create_datastore(")
    print("    name='countries',")
    print("    path='path/to/your/countries.shp',  # Your actual file path")
    print("    workspace='demo',")
    print("    use_relative_path=False")
    print(")")
    print("# This will create: file:path/to/your/countries.shp")
    
    # Example 3: Using HTTP URLs
    print("\n3. Using HTTP URLs:")
    print("geo.create_datastore(")
    print("    name='wfs_countries',")
    print("    path='http://localhost:8080/geoserver/wfs?request=GetCapabilities',")
    print("    workspace='demo'")
    print(")")
    print("# This will create: <GET_CAPABILITIES_URL>http://localhost:8080/geoserver/wfs?request=GetCapabilities</GET_CAPABILITIES_URL>")
    
    # Example 4: Cross-platform path handling
    print("\n4. Cross-platform path handling:")
    print("# The function automatically detects absolute vs relative paths")
    print("# Works on Windows, Linux, and macOS")
    print("geo.create_datastore(")
    print("    name='countries',")
    print("    path=os.path.join('/path', 'to', 'your', 'data.shp'),  # Cross-platform")
    print("    workspace='demo'")
    print(")")

if __name__ == "__main__":
    test_path_conversion() 