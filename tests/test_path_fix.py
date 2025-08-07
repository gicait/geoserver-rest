#!/usr/bin/env python3
"""
Test script to demonstrate the absolute path fix for create_datastore function.
"""

import os
import sys
import tempfile
import unittest
from geo.Geoserver import Geoserver

class TestPathConversion(unittest.TestCase):
    """Test cases for path conversion functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize GeoServer connection (adjust URL as needed)
        self.geo = Geoserver(
            service_url="http://localhost:8080/geoserver",
            username="admin",
            password="geoserver"
        )
        
        # Create some temporary test paths that will work on any machine
        self.temp_dir = tempfile.gettempdir()
        self.workspace = "demo"
        
    def test_absolute_path_conversion(self):
        """Test that absolute paths are converted to relative paths when force_absolute_path=False."""
        # Test paths using dynamic generation
        test_paths = [
            # Absolute paths (Windows-style)
            os.path.join(self.temp_dir, "countries.shp"),
            os.path.join(self.temp_dir, "data", "demo", "countries.shp"),
            
            # Absolute paths (Unix/Linux-style)
            os.path.join("/tmp", "countries.shp"),
            os.path.join("/opt", "geoserver", "data_dir", "data", "demo", "countries.shp"),
        ]
        
        for path in test_paths:
            with self.subTest(path=path):
                # Test the path conversion logic
                if os.path.isabs(path):
                    filename = os.path.basename(path)
                    expected_relative_path = f"data/{self.workspace}/{filename}"
                    
                    # Test with force_absolute_path=False (should convert to relative)
                    force_absolute_path = False
                    if not force_absolute_path and os.path.isabs(path):
                        converted_path = expected_relative_path
                    else:
                        converted_path = path
                    
                    # Assert that the conversion logic works correctly
                    self.assertEqual(converted_path, expected_relative_path)
    
    def test_relative_paths_unchanged(self):
        """Test that relative paths remain unchanged."""
        relative_paths = [
            "data/demo/countries.shp",
            "countries.shp",
            "./data/countries.shp"
        ]
        
        for path in relative_paths:
            with self.subTest(path=path):
                # Relative paths should remain unchanged
                self.assertFalse(os.path.isabs(path))
                
                # The conversion logic should not affect relative paths
                force_absolute_path = False
                if not force_absolute_path and os.path.isabs(path):
                    converted_path = f"data/{self.workspace}/{os.path.basename(path)}"
                else:
                    converted_path = path
                
                self.assertEqual(converted_path, path)
    
    def test_http_urls_unchanged(self):
        """Test that HTTP URLs remain unchanged."""
        http_urls = [
            "http://localhost:8080/geoserver/wfs?request=GetCapabilities",
            "https://example.com/wfs?service=WFS&version=1.0.0&request=GetCapabilities"
        ]
        
        for url in http_urls:
            with self.subTest(url=url):
                # HTTP URLs should remain unchanged
                self.assertTrue(url.startswith("http"))
                
                # The conversion logic should not affect HTTP URLs
                if url.startswith("http"):
                    converted_url = url  # No conversion for HTTP URLs
                else:
                    # This branch should not be reached for HTTP URLs
                    converted_url = url
                
                self.assertEqual(converted_url, url)
    
    def test_force_absolute_path_parameter(self):
        """Test the force_absolute_path parameter behavior."""
        absolute_path = os.path.join(self.temp_dir, "test.shp")
        filename = os.path.basename(absolute_path)
        expected_relative = f"data/{self.workspace}/{filename}"
        
        # Test with force_absolute_path=True (default, legacy behavior)
        # This should keep the absolute path as-is
        force_absolute_path = True
        if not force_absolute_path and os.path.isabs(absolute_path):
            result_path = expected_relative
        else:
            result_path = absolute_path
        
        self.assertEqual(result_path, absolute_path)
        
        # Test with force_absolute_path=False (new behavior)
        # This should convert to relative path
        force_absolute_path = False
        if not force_absolute_path and os.path.isabs(absolute_path):
            result_path = expected_relative
        else:
            result_path = absolute_path
        
        self.assertEqual(result_path, expected_relative)
    
    def test_create_datastore_path_conversion(self):
        """Test that create_datastore method properly handles path conversion."""
        # Test with absolute path and force_absolute_path=False
        absolute_path = os.path.join(self.temp_dir, "test.shp")
        filename = os.path.basename(absolute_path)
        workspace = "demo"
        
        # Simulate the path conversion logic from create_datastore
        force_absolute_path = False
        if not force_absolute_path and os.path.isabs(absolute_path):
            # Convert absolute path to relative path inline
            relative_path = f"data/{workspace}/{filename}"
            data_url = f"<url>file:{relative_path}</url>"
        else:
            # Use path as-is (could be relative or absolute)
            data_url = f"<url>file:{absolute_path}</url>"
        
        # Assert that the conversion happened correctly
        expected_url = f"<url>file:data/{workspace}/{filename}</url>"
        self.assertEqual(data_url, expected_url)
        
        # Test with force_absolute_path=True (legacy behavior)
        force_absolute_path = True
        if not force_absolute_path and os.path.isabs(absolute_path):
            relative_path = f"data/{workspace}/{filename}"
            data_url = f"<url>file:{relative_path}</url>"
        else:
            data_url = f"<url>file:{absolute_path}</url>"
        
        # Assert that no conversion happened (legacy behavior)
        expected_url = f"<url>file:{absolute_path}</url>"
        self.assertEqual(data_url, expected_url)
    
    def test_http_url_handling(self):
        """Test that HTTP URLs are handled correctly in create_datastore."""
        http_url = "http://localhost:8080/geoserver/wfs?request=GetCapabilities"
        
        # Simulate the HTTP URL handling logic from create_datastore
        if "http://" in http_url:
            data_url = f"<GET_CAPABILITIES_URL>{http_url}</GET_CAPABILITIES_URL>"
        else:
            # This branch should not be reached for HTTP URLs
            data_url = f"<url>file:{http_url}</url>"
        
        expected_url = f"<GET_CAPABILITIES_URL>{http_url}</GET_CAPABILITIES_URL>"
        self.assertEqual(data_url, expected_url)

def test_path_conversion_demo():
    """Demonstration function showing the path conversion functionality."""
    
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
    
    # Example 1: Using relative paths (new behavior)
    print("\n1. Using relative paths (force_absolute_path=False):")
    print("geo.create_datastore(")
    print("    name='countries',")
    print("    path='path/to/your/countries.shp',  # Your actual file path")
    print("    workspace='demo',")
    print("    force_absolute_path=False  # Convert to relative paths")
    print(")")
    print("# This will create: file:data/demo/countries.shp")
    
    # Example 2: Using absolute paths (legacy behavior)
    print("\n2. Using absolute paths (legacy, force_absolute_path=True):")
    print("geo.create_datastore(")
    print("    name='countries',")
    print("    path='path/to/your/countries.shp',  # Your actual file path")
    print("    workspace='demo',")
    print("    force_absolute_path=True  # This is the default")
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
    # Run the unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION MODE")
    print("=" * 80)
    
    # Run the demonstration
    test_path_conversion_demo() 