#!/usr/bin/env python3
"""
Simple validation script for CNC functionality in Moonraker.
This script tests the CNC API endpoints to ensure they are properly configured.
"""

import asyncio
import json
from typing import Dict, Any


class MockWebRequest:
    """Mock web request for testing"""
    def __init__(self, params: Dict[str, Any] = None):
        self.params = params or {}
    
    def get_int(self, key: str, default: int = None) -> int:
        return self.params.get(key, default)
    
    def get_str(self, key: str, default: str = None) -> str:
        return self.params.get(key, default)
    
    def get_float(self, key: str, default: float = None) -> float:
        return self.params.get(key, default)


class MockServer:
    """Mock server for testing"""
    def __init__(self):
        self.endpoints = {}
        self.error = Exception
    
    def register_endpoint(self, path: str, method: str, handler):
        self.endpoints[f"{method} {path}"] = handler
        print(f"Registered endpoint: {method} {path}")
    
    def lookup_component(self, name: str):
        return MockKlippyAPI()


class MockKlippyAPI:
    """Mock Klipper API for testing"""
    async def run_gcode(self, gcode: str) -> str:
        print(f"Would execute G-code: {gcode}")
        return f"ok: {gcode}"


class MockConfig:
    """Mock config for testing"""
    def get_server(self):
        return MockServer()


async def test_cnc_functionality():
    """Test CNC component functionality"""
    print("Testing CNC component functionality...")
    
    # Import the CNC component
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from moonraker.components.cnc import CNC
        print("✓ CNC component imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import CNC component: {e}")
        return False
    
    # Create CNC instance
    try:
        config = MockConfig()
        cnc = CNC(config)
        print("✓ CNC component instantiated successfully")
    except Exception as e:
        print(f"✗ Failed to create CNC instance: {e}")
        return False
    
    # Test spindle operations
    print("\nTesting spindle operations...")
    try:
        # Test spindle start CW
        request = MockWebRequest({"speed": 1500, "direction": "CW"})
        result = await cnc._spindle_start(request)
        assert result["spindle_running"] == True
        assert result["spindle_speed"] == 1500
        assert result["spindle_direction"] == "CW"
        print("✓ Spindle start CW test passed")
        
        # Test spindle start CCW
        request = MockWebRequest({"speed": 2000, "direction": "CCW"})
        result = await cnc._spindle_start(request)
        assert result["spindle_direction"] == "CCW"
        print("✓ Spindle start CCW test passed")
        
        # Test spindle stop
        request = MockWebRequest()
        result = await cnc._spindle_stop(request)
        assert result["spindle_running"] == False
        assert result["spindle_speed"] == 0
        print("✓ Spindle stop test passed")
        
        # Test spindle status
        status = cnc._spindle_status(request)
        assert "spindle_running" in status
        print("✓ Spindle status test passed")
        
    except Exception as e:
        print(f"✗ Spindle test failed: {e}")
        return False
    
    # Test coolant operations
    print("\nTesting coolant operations...")
    try:
        request = MockWebRequest()
        
        # Test mist coolant
        result = await cnc._coolant_mist(request)
        assert result["mist"] == True
        print("✓ Mist coolant test passed")
        
        # Test flood coolant
        result = await cnc._coolant_flood(request)
        assert result["flood"] == True
        print("✓ Flood coolant test passed")
        
        # Test coolant off
        result = await cnc._coolant_off(request)
        assert result["mist"] == False
        assert result["flood"] == False
        print("✓ Coolant off test passed")
        
        # Test coolant status
        status = cnc._coolant_status(request)
        assert "mist" in status and "flood" in status
        print("✓ Coolant status test passed")
        
    except Exception as e:
        print(f"✗ Coolant test failed: {e}")
        return False
    
    # Test tool operations
    print("\nTesting tool operations...")
    try:
        # Test tool change
        request = MockWebRequest({"tool": 5})
        result = await cnc._tool_change(request)
        assert result["current_tool"] == 5
        print("✓ Tool change test passed")
        
        # Test tool status
        request = MockWebRequest()
        status = cnc._tool_status(request)
        assert status["current_tool"] == 5
        print("✓ Tool status test passed")
        
    except Exception as e:
        print(f"✗ Tool test failed: {e}")
        return False
    
    # Test coordinate system operations
    print("\nTesting coordinate system operations...")
    try:
        # Test set coordinate system
        request = MockWebRequest({"system": "G55"})
        result = await cnc._set_coordinate_system(request)
        assert result["coordinate_system"] == "G55"
        print("✓ Set coordinate system test passed")
        
        # Test get coordinate system
        request = MockWebRequest()
        status = cnc._get_coordinate_system(request)
        assert status["coordinate_system"] == "G55"
        print("✓ Get coordinate system test passed")
        
    except Exception as e:
        print(f"✗ Coordinate system test failed: {e}")
        return False
    
    # Test probing operations
    print("\nTesting probing operations...")
    try:
        request = MockWebRequest({
            "x": 10.0,
            "y": 20.0,
            "z": -5.0,
            "feed_rate": 8.0
        })
        result = await cnc._probe(request)
        assert "gcode_executed" in result
        assert "G38.2" in result["gcode_executed"]
        print("✓ Probing test passed")
        
    except Exception as e:
        print(f"✗ Probing test failed: {e}")
        return False
    
    print("\n✓ All CNC functionality tests passed!")
    return True


def validate_api_endpoints():
    """Validate that all required API endpoints are registered"""
    print("\nValidating API endpoint registration...")
    
    config = MockConfig()
    server = config.get_server()
    
    # Import and create CNC component
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from moonraker.components.cnc import CNC
        cnc = CNC(config)
    except ImportError:
        print("✗ Cannot import CNC component for endpoint validation")
        return False
    
    expected_endpoints = [
        "POST /printer/cnc/spindle/start",
        "POST /printer/cnc/spindle/stop", 
        "GET /printer/cnc/spindle/status",
        "POST /printer/cnc/coolant/mist",
        "POST /printer/cnc/coolant/flood",
        "POST /printer/cnc/coolant/off",
        "GET /printer/cnc/coolant/status",
        "POST /printer/cnc/tool/change",
        "GET /printer/cnc/tool/status",
        "POST /printer/cnc/coordinate_system",
        "GET /printer/cnc/coordinate_system",
        "POST /printer/cnc/probe"
    ]
    
    missing_endpoints = []
    for endpoint in expected_endpoints:
        if endpoint not in server.endpoints:
            missing_endpoints.append(endpoint)
    
    if missing_endpoints:
        print(f"✗ Missing endpoints: {missing_endpoints}")
        return False
    else:
        print(f"✓ All {len(expected_endpoints)} required endpoints registered")
        return True


async def main():
    """Main validation function"""
    print("=" * 60)
    print("Moonraker CNC Feature Validation")
    print("=" * 60)
    
    # Validate endpoint registration
    endpoint_validation = validate_api_endpoints()
    
    # Test functionality
    functionality_test = await test_cnc_functionality()
    
    print("\n" + "=" * 60)
    if endpoint_validation and functionality_test:
        print("✓ ALL VALIDATION TESTS PASSED")
        print("✓ CNC features are ready for use")
    else:
        print("✗ SOME VALIDATION TESTS FAILED")
        print("✗ Please check the implementation")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())