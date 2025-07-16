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
        
        # Feed hold and pause endpoints
        self.server.register_endpoint(
            "/printer/cnc/feed_hold", RequestType.POST, self._feed_hold
        )
        self.server.register_endpoint(
            "/printer/cnc/cycle_start", RequestType.POST, self._cycle_start
        )
        self.server.register_endpoint(
            "/printer/cnc/pause_status", RequestType.GET, self._pause_status
        )
        
        # Canned cycle endpoints
        self.server.register_endpoint(
            "/printer/cnc/drilling_cycle", RequestType.POST, self._drilling_cycle
        )
        self.server.register_endpoint(
            "/printer/cnc/cancel_cycle", RequestType.POST, self._cancel_cycle
        )
        
        # Handwheel endpoints
        self.server.register_endpoint(
            "/printer/cnc/handwheel/enable", RequestType.POST, self._handwheel_enable
        )
        self.server.register_endpoint(
            "/printer/cnc/handwheel/disable", RequestType.POST, self._handwheel_disable
        )
        self.server.register_endpoint(
            "/printer/cnc/handwheel/jog", RequestType.POST, self._handwheel_jog
        )
        self.server.register_endpoint(
            "/printer/cnc/handwheel/status", RequestType.GET, self._handwheel_status
        )
        
        # Multi-axis endpoints
        self.server.register_endpoint(
            "/printer/cnc/multi_axis/status", RequestType.GET, self._multi_axis_status
        )
        self.server.register_endpoint(
            "/printer/cnc/multi_axis/home", RequestType.POST, self._multi_axis_home
        )
        
    async def _spindle_start(self, web_request: WebRequest) -> Dict[str, Any]:
        """Start spindle with specified speed and direction"""
        speed: int = web_request.get_int("speed", default=1000)
        direction: str = web_request.get_str("direction", default="CW")
        
        # Validate speed range
        if speed < 0 or speed > 30000:
            raise self.server.error("Spindle speed must be between 0 and 30000 RPM")
        
        if direction not in ["CW", "CCW"]:
            raise self.server.error("Invalid spindle direction. Must be 'CW' or 'CCW'")
            
        # Execute appropriate gcode command using Klipper spindle extra
        if direction == "CW":
            gcode = f"M3 S{speed}"
        else:
            gcode = f"M4 S{speed}"
            
        try:
            result = await self.klippy_apis.run_gcode(gcode)
        except Exception as e:
            raise self.server.error(f"Failed to start spindle: {e}")
        
        # Get current status from Klipper spindle extra
        status = await self._get_spindle_status_from_klipper()
        
        return {
            "result": "ok",
            **status
        }
        
    async def _spindle_stop(self, web_request: WebRequest) -> Dict[str, Any]:
        """Stop spindle"""
        try:
            result = await self.klippy_apis.run_gcode("M5")
        except Exception as e:
            raise self.server.error(f"Failed to stop spindle: {e}")
        
        # Get current status from Klipper spindle extra
        status = await self._get_spindle_status_from_klipper()
        
        return {
            "result": "ok",
            **status
        }
        
    async def _spindle_status(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get spindle status"""
        return await self._get_spindle_status_from_klipper()
    
    async def _get_spindle_status_from_klipper(self) -> Dict[str, Any]:
        """Get spindle status from Klipper spindle extra"""
        try:
            # Query the spindle object status from Klipper
            result = await self.klippy_apis.query_objects({"spindle": None})
            if "spindle" in result:
                spindle_status = result["spindle"]
                return {
                    "spindle_running": spindle_status.get("enabled", False),
                    "spindle_speed": spindle_status.get("speed", 0),
                    "spindle_direction": spindle_status.get("direction", "CW")
                }
            else:
                # Fallback if spindle extra not configured
                return {
                    "spindle_running": False,
                    "spindle_speed": 0,
                    "spindle_direction": "CW",
                    "error": "Spindle not configured in Klipper"
                }
        except Exception as e:
            # Return default values if query fails
            return {
                "spindle_running": False,
                "spindle_speed": 0,
                "spindle_direction": "CW",
                "error": f"Failed to query spindle status: {e}"
            }
        
    async def _coolant_mist(self, web_request: WebRequest) -> Dict[str, Any]:
        """Turn on mist coolant"""
        try:
            result = await self.klippy_apis.run_gcode("M7")
        except Exception as e:
            raise self.server.error(f"Failed to turn on mist coolant: {e}")
        
        # Get current status from Klipper coolant extra
        status = await self._get_coolant_status_from_klipper()
        return {"result": "ok", **status}
        
    async def _coolant_flood(self, web_request: WebRequest) -> Dict[str, Any]:
        """Turn on flood coolant"""
        try:
            result = await self.klippy_apis.run_gcode("M8")
        except Exception as e:
            raise self.server.error(f"Failed to turn on flood coolant: {e}")
        
        # Get current status from Klipper coolant extra
        status = await self._get_coolant_status_from_klipper()
        return {"result": "ok", **status}
        
    async def _coolant_off(self, web_request: WebRequest) -> Dict[str, Any]:
        """Turn off all coolant"""
        try:
            result = await self.klippy_apis.run_gcode("M9")
        except Exception as e:
            raise self.server.error(f"Failed to turn off coolant: {e}")
        
        # Get current status from Klipper coolant extra
        status = await self._get_coolant_status_from_klipper()
        return {"result": "ok", **status}
        
    async def _coolant_status(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get coolant status"""
        return await self._get_coolant_status_from_klipper()
    
    async def _get_coolant_status_from_klipper(self) -> Dict[str, Any]:
        """Get coolant status from Klipper coolant extra"""
        try:
            # Query the coolant object status from Klipper
            result = await self.klippy_apis.query_objects({"coolant": None})
            if "coolant" in result:
                coolant_status = result["coolant"]
                return {
                    "mist": coolant_status.get("mist", False),
                    "flood": coolant_status.get("flood", False)
                }
            else:
                # Fallback if coolant extra not configured
                return {
                    "mist": False,
                    "flood": False,
                    "error": "Coolant not configured in Klipper"
                }
        except Exception as e:
            # Return default values if query fails
            return {
                "mist": False,
                "flood": False,
                "error": f"Failed to query coolant status: {e}"
            }
        
    async def _tool_change(self, web_request: WebRequest) -> Dict[str, Any]:
        """Change tool"""
        tool_number: int = web_request.get_int("tool")
        
        # Validate tool number range
        if tool_number < 0 or tool_number > 999:
            raise self.server.error("Tool number must be between 0 and 999")
        
        # Execute tool change using Klipper tool_change extra
        gcode = f"T{tool_number}"
        try:
            result = await self.klippy_apis.run_gcode(gcode)
        except Exception as e:
            raise self.server.error(f"Failed to change tool: {e}")
        
        # Get current status from Klipper tool_change extra
        status = await self._get_tool_status_from_klipper()
        return {"result": "ok", **status}
        
    async def _tool_status(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get current tool"""
        return await self._get_tool_status_from_klipper()
    
    async def _get_tool_status_from_klipper(self) -> Dict[str, Any]:
        """Get tool status from Klipper tool_change extra"""
        try:
            # Query the tool_change object status from Klipper
            result = await self.klippy_apis.query_objects({"tool_change": None})
            if "tool_change" in result:
                tool_status = result["tool_change"]
                return {
                    "current_tool": tool_status.get("current_tool", 0),
                    "max_tool": tool_status.get("max_tool", 99)
                }
            else:
                # Fallback if tool_change extra not configured
                return {
                    "current_tool": 0,
                    "max_tool": 99,
                    "error": "Tool change not configured in Klipper"
                }
        except Exception as e:
            # Return default values if query fails
            return {
                "current_tool": 0,
                "max_tool": 99,
                "error": f"Failed to query tool status: {e}"
            }
        
    async def _set_coordinate_system(self, web_request: WebRequest) -> Dict[str, Any]:
        """Set coordinate system (G54-G59)"""
        system: str = web_request.get_str("system")
        
        valid_systems = ["G54", "G55", "G56", "G57", "G58", "G59"]
        if system not in valid_systems:
            raise self.server.error(f"Invalid coordinate system. Must be one of: {valid_systems}")
        
        try:
            result = await self.klippy_apis.run_gcode(system)
        except Exception as e:
            raise self.server.error(f"Failed to set coordinate system: {e}")
        
        # Get current status from Klipper work_coordinate_systems extra
        status = await self._get_coordinate_system_status_from_klipper()
        return {"result": "ok", **status}
        
    async def _get_coordinate_system(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get current coordinate system"""
        return await self._get_coordinate_system_status_from_klipper()
    
    async def _get_coordinate_system_status_from_klipper(self) -> Dict[str, Any]:
        """Get coordinate system status from Klipper work_coordinate_systems extra"""
        try:
            # Query the work_coordinate_systems object status from Klipper
            result = await self.klippy_apis.query_objects({"work_coordinate_systems": None})
            if "work_coordinate_systems" in result:
                wcs_status = result["work_coordinate_systems"]
                return {
                    "coordinate_system": f"G{wcs_status.get('active_system', 54)}",
                    "coordinate_systems": wcs_status.get("coordinate_systems", {})
                }
            else:
                # Fallback if work_coordinate_systems extra not configured
                return {
                    "coordinate_system": "G54",
                    "coordinate_systems": {},
                    "error": "Work coordinate systems not configured in Klipper"
                }
        except Exception as e:
            # Return default values if query fails
            return {
                "coordinate_system": "G54",
                "coordinate_systems": {},
                "error": f"Failed to query coordinate system status: {e}"
            }
        
    async def _probe(self, web_request: WebRequest) -> Dict[str, Any]:
        """Execute probing operation"""
        # Get probe parameters
        x: Optional[float] = web_request.get_float("x", None)
        y: Optional[float] = web_request.get_float("y", None) 
        z: Optional[float] = web_request.get_float("z", None)
        feed_rate: float = web_request.get_float("feed_rate", default=5.0)
        
        # Build probe command using Klipper cnc_probing extra
        gcode_parts = ["G38.2"]
        if x is not None:
            gcode_parts.append(f"X{x}")
        if y is not None:
            gcode_parts.append(f"Y{y}")
        if z is not None:
            gcode_parts.append(f"Z{z}")
        gcode_parts.append(f"F{feed_rate * 60}")  # Convert to mm/min
        
        gcode = " ".join(gcode_parts)
        
        try:
            result = await self.klippy_apis.run_gcode(gcode)
        except Exception as e:
            raise self.server.error(f"Failed to execute probe: {e}")
        
        # Get probe results from Klipper cnc_probing extra
        probe_status = await self._get_probe_status_from_klipper()
        
        return {
            "result": "ok", 
            "gcode_executed": gcode,
            **probe_status
        }
    
    async def _get_probe_status_from_klipper(self) -> Dict[str, Any]:
        """Get probe status from Klipper cnc_probing extra"""
        try:
            # Query the cnc_probing object status from Klipper
            result = await self.klippy_apis.query_objects({"cnc_probing": None})
            if "cnc_probing" in result:
                probe_status = result["cnc_probing"]
                return {
                    "last_probe": probe_status.get("last_probe", [0., 0., 0.]),
                    "probe_pin_state": probe_status.get("probe_pin_state", False)
                }
            else:
                # Fallback if cnc_probing extra not configured
                return {
                    "last_probe": [0., 0., 0.],
                    "probe_pin_state": False,
                    "error": "CNC probing not configured in Klipper"
                }
        except Exception as e:
            # Return default values if query fails
            return {
                "last_probe": [0., 0., 0.],
                "probe_pin_state": False,
                "error": f"Failed to query probe status: {e}"
            }
    
    # Feed Hold and Pause Methods
    async def _feed_hold(self, web_request: WebRequest) -> Dict[str, Any]:
        """Execute feed hold"""
        try:
            result = await self.klippy_apis.run_gcode("FEED_HOLD")
        except Exception as e:
            raise self.server.error(f"Failed to execute feed hold: {e}")
        
        status = await self._get_feed_hold_status_from_klipper()
        return {"result": "ok", **status}
    
    async def _cycle_start(self, web_request: WebRequest) -> Dict[str, Any]:
        """Resume from feed hold or pause"""
        try:
            result = await self.klippy_apis.run_gcode("CYCLE_START")
        except Exception as e:
            raise self.server.error(f"Failed to start cycle: {e}")
        
        status = await self._get_feed_hold_status_from_klipper()
        return {"result": "ok", **status}
    
    async def _pause_status(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get pause/feed hold status"""
        return await self._get_feed_hold_status_from_klipper()
    
    async def _get_feed_hold_status_from_klipper(self) -> Dict[str, Any]:
        """Get feed hold status from Klipper feed_hold extra"""
        try:
            result = await self.klippy_apis.query_objects({"feed_hold": None})
            if "feed_hold" in result:
                feed_hold_status = result["feed_hold"]
                return {
                    "is_paused": feed_hold_status.get("is_paused", False),
                    "pause_position": feed_hold_status.get("pause_position", None),
                    "feed_hold_pin_state": feed_hold_status.get("feed_hold_pin_state", None)
                }
            else:
                return {
                    "is_paused": False,
                    "pause_position": None,
                    "feed_hold_pin_state": None,
                    "error": "Feed hold not configured in Klipper"
                }
        except Exception as e:
            return {
                "is_paused": False,
                "pause_position": None,
                "feed_hold_pin_state": None,
                "error": f"Failed to query feed hold status: {e}"
            }
    
    # Canned Cycle Methods
    async def _drilling_cycle(self, web_request: WebRequest) -> Dict[str, Any]:
        """Execute drilling cycle"""
        cycle_type: str = web_request.get_str("type", default="G81")
        x: Optional[float] = web_request.get_float("x", None)
        y: Optional[float] = web_request.get_float("y", None)
        z: float = web_request.get_float("z")
        r: float = web_request.get_float("r")
        f: float = web_request.get_float("f", default=100)
        
        # Additional parameters for specific cycles
        p: Optional[float] = web_request.get_float("p", None)  # Dwell time for G82
        q: Optional[float] = web_request.get_float("q", None)  # Peck depth for G83
        
        valid_cycles = ["G81", "G82", "G83"]
        if cycle_type not in valid_cycles:
            raise self.server.error(f"Invalid cycle type. Must be one of: {valid_cycles}")
        
        # Build drilling cycle command
        gcode_parts = [cycle_type]
        if x is not None:
            gcode_parts.append(f"X{x}")
        if y is not None:
            gcode_parts.append(f"Y{y}")
        gcode_parts.extend([f"Z{z}", f"R{r}", f"F{f}"])
        
        if cycle_type == "G82" and p is not None:
            gcode_parts.append(f"P{p}")
        elif cycle_type == "G83" and q is not None:
            gcode_parts.append(f"Q{q}")
        
        gcode = " ".join(gcode_parts)
        
        try:
            result = await self.klippy_apis.run_gcode(gcode)
        except Exception as e:
            raise self.server.error(f"Failed to execute drilling cycle: {e}")
        
        return {"result": "ok", "gcode_executed": gcode}
    
    async def _cancel_cycle(self, web_request: WebRequest) -> Dict[str, Any]:
        """Cancel canned cycle"""
        try:
            result = await self.klippy_apis.run_gcode("G80")
        except Exception as e:
            raise self.server.error(f"Failed to cancel cycle: {e}")
        
        return {"result": "ok", "gcode_executed": "G80"}
    
    # Handwheel Methods
    async def _handwheel_enable(self, web_request: WebRequest) -> Dict[str, Any]:
        """Enable handwheel control"""
        try:
            result = await self.klippy_apis.run_gcode("HANDWHEEL_ENABLE")
        except Exception as e:
            raise self.server.error(f"Failed to enable handwheel: {e}")
        
        status = await self._get_handwheel_status_from_klipper()
        return {"result": "ok", **status}
    
    async def _handwheel_disable(self, web_request: WebRequest) -> Dict[str, Any]:
        """Disable handwheel control"""
        try:
            result = await self.klippy_apis.run_gcode("HANDWHEEL_DISABLE")
        except Exception as e:
            raise self.server.error(f"Failed to disable handwheel: {e}")
        
        status = await self._get_handwheel_status_from_klipper()
        return {"result": "ok", **status}
    
    async def _handwheel_jog(self, web_request: WebRequest) -> Dict[str, Any]:
        """Manual jog using handwheel"""
        axis: str = web_request.get_str("axis", default="x").upper()
        distance: float = web_request.get_float("distance")
        
        valid_axes = ["X", "Y", "Z", "A", "B", "E"]
        if axis not in valid_axes:
            raise self.server.error(f"Invalid axis. Must be one of: {valid_axes}")
        
        gcode = f"HANDWHEEL_JOG AXIS={axis} DISTANCE={distance}"
        
        try:
            result = await self.klippy_apis.run_gcode(gcode)
        except Exception as e:
            raise self.server.error(f"Failed to jog handwheel: {e}")
        
        return {"result": "ok", "gcode_executed": gcode}
    
    async def _handwheel_status(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get handwheel status"""
        return await self._get_handwheel_status_from_klipper()
    
    async def _get_handwheel_status_from_klipper(self) -> Dict[str, Any]:
        """Get handwheel status from Klipper handwheel extra"""
        try:
            result = await self.klippy_apis.query_objects({"handwheel": None})
            if "handwheel" in result:
                handwheel_status = result["handwheel"]
                return {
                    "enabled": handwheel_status.get("enabled", False),
                    "active_axis": handwheel_status.get("active_axis", "x"),
                    "step_size": handwheel_status.get("step_size", 0.1),
                    "encoder_position": handwheel_status.get("encoder_position", 0)
                }
            else:
                return {
                    "enabled": False,
                    "active_axis": "x",
                    "step_size": 0.1,
                    "encoder_position": 0,
                    "error": "Handwheel not configured in Klipper"
                }
        except Exception as e:
            return {
                "enabled": False,
                "active_axis": "x",
                "step_size": 0.1,
                "encoder_position": 0,
                "error": f"Failed to query handwheel status: {e}"
            }
    
    # Multi-Axis Methods
    async def _multi_axis_status(self, web_request: WebRequest) -> Dict[str, Any]:
        """Get multi-axis status"""
        return await self._get_multi_axis_status_from_klipper()
    
    async def _multi_axis_home(self, web_request: WebRequest) -> Dict[str, Any]:
        """Home rotary axis"""
        axis: str = web_request.get_str("axis", default="A").upper()
        
        valid_axes = ["A", "B"]
        if axis not in valid_axes:
            raise self.server.error(f"Invalid rotary axis. Must be one of: {valid_axes}")
        
        gcode = f"G28.{axis}"
        
        try:
            result = await self.klippy_apis.run_gcode(gcode)
        except Exception as e:
            raise self.server.error(f"Failed to home {axis} axis: {e}")
        
        status = await self._get_multi_axis_status_from_klipper()
        return {"result": "ok", "gcode_executed": gcode, **status}
    
    async def _get_multi_axis_status_from_klipper(self) -> Dict[str, Any]:
        """Get multi-axis status from Klipper multi_axis extra"""
        try:
            result = await self.klippy_apis.query_objects({"multi_axis": None})
            if "multi_axis" in result:
                multi_axis_status = result["multi_axis"]
                return {
                    "extra_axes": multi_axis_status.get("extra_axes", []),
                    "axis_limits": multi_axis_status.get("axis_limits", {}),
                    "accel_limited_axes": multi_axis_status.get("accel_limited_axes", []),
                    "axis_max_accel": multi_axis_status.get("axis_max_accel", {})
                }
            else:
                return {
                    "extra_axes": [],
                    "axis_limits": {},
                    "accel_limited_axes": [],
                    "axis_max_accel": {},
                    "error": "Multi-axis not configured in Klipper"
                }
        except Exception as e:
            return {
                "extra_axes": [],
                "axis_limits": {},
                "accel_limited_axes": [],
                "axis_max_accel": {},
                "error": f"Failed to query multi-axis status: {e}"
            }

def load_component(config: ConfigHelper) -> CNC:
    return CNC(config)