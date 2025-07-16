# CNC control component for moonraker
#
# Copyright (C) 2024 Eric Callahan <arksine.code@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license

from __future__ import annotations
import logging
from ..common import RequestType

# Annotation imports
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
)

if TYPE_CHECKING:
    from ..confighelper import ConfigHelper
    from ..common import WebRequest
    from .klippy_apis import KlippyAPI

class CNC:
    def __init__(self, config: ConfigHelper) -> None:
        self.server = config.get_server()
        self.klippy_apis: KlippyAPI = self.server.lookup_component("klippy_apis")
        
        # CNC state tracking
        self.spindle_running = False
        self.spindle_speed = 0
        self.spindle_direction = "CW"  # CW or CCW
        self.coolant_mist = False
        self.coolant_flood = False
        self.current_tool = 0
        self.coordinate_system = "G54"  # Default to G54
        
        # Register CNC API endpoints
        self._register_endpoints()
        
    def _register_endpoints(self) -> None:
        # Spindle control endpoints
        self.server.register_endpoint(
            "/printer/cnc/spindle/start", RequestType.POST, self._spindle_start
        )
        self.server.register_endpoint(
            "/printer/cnc/spindle/stop", RequestType.POST, self._spindle_stop
        )
        self.server.register_endpoint(
            "/printer/cnc/spindle/status", RequestType.GET, self._spindle_status
        )
        
        # Coolant control endpoints  
        self.server.register_endpoint(
            "/printer/cnc/coolant/mist", RequestType.POST, self._coolant_mist
        )
        self.server.register_endpoint(
            "/printer/cnc/coolant/flood", RequestType.POST, self._coolant_flood
        )
        self.server.register_endpoint(
            "/printer/cnc/coolant/off", RequestType.POST, self._coolant_off
        )
        self.server.register_endpoint(
            "/printer/cnc/coolant/status", RequestType.GET, self._coolant_status
        )
        
        # Tool control endpoints
        self.server.register_endpoint(
            "/printer/cnc/tool/change", RequestType.POST, self._tool_change
        )
        self.server.register_endpoint(
            "/printer/cnc/tool/status", RequestType.GET, self._tool_status
        )
        
        # Coordinate system endpoints
        self.server.register_endpoint(
            "/printer/cnc/coordinate_system", RequestType.POST, self._set_coordinate_system
        )
        self.server.register_endpoint(
            "/printer/cnc/coordinate_system", RequestType.GET, self._get_coordinate_system
        )
        
        # Probing endpoints
        self.server.register_endpoint(
            "/printer/cnc/probe", RequestType.POST, self._probe
        )
        
    async def _spindle_start(self, web_request: WebRequest) -> Dict[str, Any]:
        """Start spindle with specified speed and direction"""
        speed: int = web_request.get_int("speed", default=1000)
        direction: str = web_request.get_str("direction", default="CW")
        
        if direction not in ["CW", "CCW"]:
            raise self.server.error("Invalid spindle direction. Must be 'CW' or 'CCW'")
            
        # Execute appropriate gcode command
        if direction == "CW":
            gcode = f"M3 S{speed}"
        else:
            gcode = f"M4 S{speed}"
            
        result = await self.klippy_apis.run_gcode(gcode)
        
        # Update state
        self.spindle_running = True
        self.spindle_speed = speed
        self.spindle_direction = direction
        
        return {
            "result": "ok",
            "spindle_running": self.spindle_running,
            "spindle_speed": self.spindle_speed,
            "spindle_direction": self.spindle_direction
        }
        
    async def _spindle_stop(self, web_request: WebRequest) -> Dict[str, Any]:
        """Stop spindle"""
        result = await self.klippy_apis.run_gcode("M5")
        
        # Update state
        self.spindle_running = False
        self.spindle_speed = 0
        
        return {
            "result": "ok",
            "spindle_running": self.spindle_running,
            "spindle_speed": self.spindle_speed
        }
        
    async def _spindle_status(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get spindle status"""
        return {
            "spindle_running": self.spindle_running,
            "spindle_speed": self.spindle_speed,
            "spindle_direction": self.spindle_direction
        }
        
    async def _coolant_mist(self, web_request: WebRequest) -> Dict[str, Any]:
        """Turn on mist coolant"""
        result = await self.klippy_apis.run_gcode("M7")
        self.coolant_mist = True
        return {"result": "ok", "mist": True}
        
    async def _coolant_flood(self, web_request: WebRequest) -> Dict[str, Any]:
        """Turn on flood coolant"""
        result = await self.klippy_apis.run_gcode("M8") 
        self.coolant_flood = True
        return {"result": "ok", "flood": True}
        
    async def _coolant_off(self, web_request: WebRequest) -> Dict[str, Any]:
        """Turn off all coolant"""
        result = await self.klippy_apis.run_gcode("M9")
        self.coolant_mist = False
        self.coolant_flood = False
        return {"result": "ok", "mist": False, "flood": False}
        
    async def _coolant_status(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get coolant status"""
        return {
            "mist": self.coolant_mist,
            "flood": self.coolant_flood
        }
        
    async def _tool_change(self, web_request: WebRequest) -> Dict[str, Any]:
        """Change tool"""
        tool_number: int = web_request.get_int("tool")
        
        # Execute tool change gcode
        gcode = f"T{tool_number}"
        result = await self.klippy_apis.run_gcode(gcode)
        
        self.current_tool = tool_number
        return {"result": "ok", "current_tool": self.current_tool}
        
    async def _tool_status(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get current tool"""
        return {"current_tool": self.current_tool}
        
    async def _set_coordinate_system(self, web_request: WebRequest) -> Dict[str, Any]:
        """Set coordinate system (G54-G59)"""
        system: str = web_request.get_str("system")
        
        valid_systems = ["G54", "G55", "G56", "G57", "G58", "G59"]
        if system not in valid_systems:
            raise self.server.error(f"Invalid coordinate system. Must be one of: {valid_systems}")
            
        result = await self.klippy_apis.run_gcode(system)
        self.coordinate_system = system
        return {"result": "ok", "coordinate_system": self.coordinate_system}
        
    async def _get_coordinate_system(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get current coordinate system"""
        return {"coordinate_system": self.coordinate_system}
        
    async def _probe(self, web_request: WebRequest) -> Dict[str, Any]:
        """Execute probing operation"""
        # Get probe parameters
        x: Optional[float] = web_request.get_float("x", None)
        y: Optional[float] = web_request.get_float("y", None) 
        z: Optional[float] = web_request.get_float("z", None)
        feed_rate: float = web_request.get_float("feed_rate", default=5.0)
        
        # Build probe command
        gcode_parts = ["G38.2"]
        if x is not None:
            gcode_parts.append(f"X{x}")
        if y is not None:
            gcode_parts.append(f"Y{y}")
        if z is not None:
            gcode_parts.append(f"Z{z}")
        gcode_parts.append(f"F{feed_rate}")
        
        gcode = " ".join(gcode_parts)
        result = await self.klippy_apis.run_gcode(gcode)
        
        return {"result": "ok", "gcode_executed": gcode}

def load_component(config: ConfigHelper) -> CNC:
    return CNC(config)