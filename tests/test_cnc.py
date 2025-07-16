# Test CNC component functionality
#
# Copyright (C) 2024 Eric Callahan <arksine.code@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license

import pytest
from unittest.mock import AsyncMock, MagicMock
from moonraker.components.cnc import CNC


class TestCNC:
    @pytest.fixture
    def mock_config(self):
        """Mock config helper"""
        config = MagicMock()
        server = MagicMock()
        klippy_apis = AsyncMock()
        
        config.get_server.return_value = server
        server.lookup_component.return_value = klippy_apis
        server.register_endpoint = MagicMock()
        server.error = Exception
        
        return config, server, klippy_apis

    @pytest.fixture
    def cnc_component(self, mock_config):
        """Create CNC component instance"""
        config, server, klippy_apis = mock_config
        return CNC(config), server, klippy_apis

    @pytest.mark.asyncio
    async def test_spindle_start_cw(self, cnc_component):
        """Test starting spindle clockwise"""
        cnc, server, klippy_apis = cnc_component
        
        # Mock web request
        web_request = MagicMock()
        web_request.get_int.return_value = 1500
        web_request.get_str.return_value = "CW"
        
        # Mock klippy_apis.run_gcode
        klippy_apis.run_gcode.return_value = "ok"
        
        result = await cnc._spindle_start(web_request)
        
        # Verify gcode was called correctly
        klippy_apis.run_gcode.assert_called_with("M3 S1500")
        
        # Verify state was updated
        assert cnc.spindle_running == True
        assert cnc.spindle_speed == 1500
        assert cnc.spindle_direction == "CW"
        
        # Verify response
        assert result["result"] == "ok"
        assert result["spindle_running"] == True
        assert result["spindle_speed"] == 1500
        assert result["spindle_direction"] == "CW"

    @pytest.mark.asyncio
    async def test_spindle_start_ccw(self, cnc_component):
        """Test starting spindle counter-clockwise"""
        cnc, server, klippy_apis = cnc_component
        
        # Mock web request
        web_request = MagicMock()
        web_request.get_int.return_value = 2000
        web_request.get_str.return_value = "CCW"
        
        # Mock klippy_apis.run_gcode
        klippy_apis.run_gcode.return_value = "ok"
        
        result = await cnc._spindle_start(web_request)
        
        # Verify gcode was called correctly
        klippy_apis.run_gcode.assert_called_with("M4 S2000")
        
        # Verify state was updated
        assert cnc.spindle_running == True
        assert cnc.spindle_speed == 2000
        assert cnc.spindle_direction == "CCW"

    @pytest.mark.asyncio
    async def test_spindle_stop(self, cnc_component):
        """Test stopping spindle"""
        cnc, server, klippy_apis = cnc_component
        
        # Set initial state
        cnc.spindle_running = True
        cnc.spindle_speed = 1500
        
        # Mock web request
        web_request = MagicMock()
        
        # Mock klippy_apis.run_gcode
        klippy_apis.run_gcode.return_value = "ok"
        
        result = await cnc._spindle_stop(web_request)
        
        # Verify gcode was called correctly
        klippy_apis.run_gcode.assert_called_with("M5")
        
        # Verify state was updated
        assert cnc.spindle_running == False
        assert cnc.spindle_speed == 0
        
        # Verify response
        assert result["result"] == "ok"
        assert result["spindle_running"] == False

    @pytest.mark.asyncio
    async def test_coolant_mist(self, cnc_component):
        """Test turning on mist coolant"""
        cnc, server, klippy_apis = cnc_component
        
        # Mock web request
        web_request = MagicMock()
        
        # Mock klippy_apis.run_gcode
        klippy_apis.run_gcode.return_value = "ok"
        
        result = await cnc._coolant_mist(web_request)
        
        # Verify gcode was called correctly
        klippy_apis.run_gcode.assert_called_with("M7")
        
        # Verify state was updated
        assert cnc.coolant_mist == True
        
        # Verify response
        assert result["result"] == "ok"
        assert result["mist"] == True

    @pytest.mark.asyncio
    async def test_coolant_flood(self, cnc_component):
        """Test turning on flood coolant"""
        cnc, server, klippy_apis = cnc_component
        
        # Mock web request
        web_request = MagicMock()
        
        # Mock klippy_apis.run_gcode
        klippy_apis.run_gcode.return_value = "ok"
        
        result = await cnc._coolant_flood(web_request)
        
        # Verify gcode was called correctly
        klippy_apis.run_gcode.assert_called_with("M8")
        
        # Verify state was updated
        assert cnc.coolant_flood == True
        
        # Verify response
        assert result["result"] == "ok"
        assert result["flood"] == True

    @pytest.mark.asyncio
    async def test_coolant_off(self, cnc_component):
        """Test turning off all coolant"""
        cnc, server, klippy_apis = cnc_component
        
        # Set initial state
        cnc.coolant_mist = True
        cnc.coolant_flood = True
        
        # Mock web request
        web_request = MagicMock()
        
        # Mock klippy_apis.run_gcode
        klippy_apis.run_gcode.return_value = "ok"
        
        result = await cnc._coolant_off(web_request)
        
        # Verify gcode was called correctly
        klippy_apis.run_gcode.assert_called_with("M9")
        
        # Verify state was updated
        assert cnc.coolant_mist == False
        assert cnc.coolant_flood == False
        
        # Verify response
        assert result["result"] == "ok"
        assert result["mist"] == False
        assert result["flood"] == False

    @pytest.mark.asyncio
    async def test_tool_change(self, cnc_component):
        """Test tool change"""
        cnc, server, klippy_apis = cnc_component
        
        # Mock web request
        web_request = MagicMock()
        web_request.get_int.return_value = 5
        
        # Mock klippy_apis.run_gcode
        klippy_apis.run_gcode.return_value = "ok"
        
        result = await cnc._tool_change(web_request)
        
        # Verify gcode was called correctly
        klippy_apis.run_gcode.assert_called_with("T5")
        
        # Verify state was updated
        assert cnc.current_tool == 5
        
        # Verify response
        assert result["result"] == "ok"
        assert result["current_tool"] == 5

    @pytest.mark.asyncio
    async def test_coordinate_system_change(self, cnc_component):
        """Test coordinate system change"""
        cnc, server, klippy_apis = cnc_component
        
        # Mock web request
        web_request = MagicMock()
        web_request.get_str.return_value = "G55"
        
        # Mock klippy_apis.run_gcode
        klippy_apis.run_gcode.return_value = "ok"
        
        result = await cnc._set_coordinate_system(web_request)
        
        # Verify gcode was called correctly
        klippy_apis.run_gcode.assert_called_with("G55")
        
        # Verify state was updated
        assert cnc.coordinate_system == "G55"
        
        # Verify response
        assert result["result"] == "ok"
        assert result["coordinate_system"] == "G55"

    @pytest.mark.asyncio
    async def test_probe(self, cnc_component):
        """Test probing operation"""
        cnc, server, klippy_apis = cnc_component
        
        # Mock web request
        web_request = MagicMock()
        web_request.get_float.side_effect = lambda key, default=None: {
            "x": 10.0,
            "y": 20.0, 
            "z": -5.0,
            "feed_rate": 8.0
        }.get(key, default)
        
        # Mock klippy_apis.run_gcode
        klippy_apis.run_gcode.return_value = "ok"
        
        result = await cnc._probe(web_request)
        
        # Verify gcode was called correctly
        klippy_apis.run_gcode.assert_called_with("G38.2 X10.0 Y20.0 Z-5.0 F8.0")
        
        # Verify response
        assert result["result"] == "ok"
        assert result["gcode_executed"] == "G38.2 X10.0 Y20.0 Z-5.0 F8.0"

    def test_status_endpoints(self, cnc_component):
        """Test status endpoints"""
        cnc, server, klippy_apis = cnc_component
        
        # Set some state
        cnc.spindle_running = True
        cnc.spindle_speed = 1200
        cnc.spindle_direction = "CW"
        cnc.coolant_mist = True
        cnc.coolant_flood = False
        cnc.current_tool = 3
        cnc.coordinate_system = "G56"
        
        # Mock web request
        web_request = MagicMock()
        
        # Test spindle status
        spindle_status = cnc._spindle_status(web_request)
        assert spindle_status["spindle_running"] == True
        assert spindle_status["spindle_speed"] == 1200
        assert spindle_status["spindle_direction"] == "CW"
        
        # Test coolant status
        coolant_status = cnc._coolant_status(web_request)
        assert coolant_status["mist"] == True
        assert coolant_status["flood"] == False
        
        # Test tool status
        tool_status = cnc._tool_status(web_request)
        assert tool_status["current_tool"] == 3
        
        # Test coordinate system status
        coord_status = cnc._get_coordinate_system(web_request)
        assert coord_status["coordinate_system"] == "G56"