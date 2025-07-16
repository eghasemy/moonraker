#!/usr/bin/env python3
"""
Example CNC workflow using Moonraker CNC API
This script demonstrates a typical CNC milling operation workflow.

PREREQUISITES:
- Klipper with CNC extras configured (spindle, coolant, tool_change, etc.)
- Moonraker with [cnc] section enabled
- Proper hardware connections for spindle, coolant, and probing

This example interfaces with Moonraker's CNC API endpoints, which in turn
communicate with Klipper's CNC extras to provide the actual functionality.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any


class MoonrakerCNC:
    """Client for Moonraker CNC API"""
    
    def __init__(self, host: str = "localhost", port: int = 7125):
        self.base_url = f"http://{host}:{port}"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make POST request to Moonraker"""
        url = f"{self.base_url}{endpoint}"
        async with self.session.post(url, data=data) as response:
            return await response.json()
    
    async def _get(self, endpoint: str) -> Dict[str, Any]:
        """Make GET request to Moonraker"""
        url = f"{self.base_url}{endpoint}"
        async with self.session.get(url) as response:
            return await response.json()
    
    # Spindle control methods
    async def start_spindle(self, speed: int = 1000, direction: str = "CW") -> Dict[str, Any]:
        """Start spindle with specified speed and direction"""
        return await self._post("/printer/cnc/spindle/start", {
            "speed": speed,
            "direction": direction
        })
    
    async def stop_spindle(self) -> Dict[str, Any]:
        """Stop spindle"""
        return await self._post("/printer/cnc/spindle/stop")
    
    async def get_spindle_status(self) -> Dict[str, Any]:
        """Get spindle status"""
        return await self._get("/printer/cnc/spindle/status")
    
    # Coolant control methods
    async def coolant_mist_on(self) -> Dict[str, Any]:
        """Turn on mist coolant"""
        return await self._post("/printer/cnc/coolant/mist")
    
    async def coolant_flood_on(self) -> Dict[str, Any]:
        """Turn on flood coolant"""
        return await self._post("/printer/cnc/coolant/flood")
    
    async def coolant_off(self) -> Dict[str, Any]:
        """Turn off all coolant"""
        return await self._post("/printer/cnc/coolant/off")
    
    async def get_coolant_status(self) -> Dict[str, Any]:
        """Get coolant status"""
        return await self._get("/printer/cnc/coolant/status")
    
    # Tool control methods
    async def change_tool(self, tool_number: int) -> Dict[str, Any]:
        """Change to specified tool"""
        return await self._post("/printer/cnc/tool/change", {
            "tool": tool_number
        })
    
    async def get_current_tool(self) -> Dict[str, Any]:
        """Get current tool number"""
        return await self._get("/printer/cnc/tool/status")
    
    # Coordinate system methods
    async def set_coordinate_system(self, system: str) -> Dict[str, Any]:
        """Set coordinate system (G54-G59)"""
        return await self._post("/printer/cnc/coordinate_system", {
            "system": system
        })
    
    async def get_coordinate_system(self) -> Dict[str, Any]:
        """Get current coordinate system"""
        return await self._get("/printer/cnc/coordinate_system")
    
    # Probing methods
    async def probe(self, x: float = None, y: float = None, z: float = None, 
                   feed_rate: float = 5.0) -> Dict[str, Any]:
        """Execute probing operation"""
        data = {"feed_rate": feed_rate}
        if x is not None:
            data["x"] = x
        if y is not None:
            data["y"] = y
        if z is not None:
            data["z"] = z
        return await self._post("/printer/cnc/probe", data)
    
    # G-code execution
    async def execute_gcode(self, script: str) -> Dict[str, Any]:
        """Execute arbitrary G-code script"""
        return await self._post("/printer/gcode/script", {"script": script})
    
    # Emergency stop
    async def emergency_stop(self) -> Dict[str, Any]:
        """Execute emergency stop"""
        return await self._post("/printer/cnc/emergency_stop")


async def cnc_workflow_example():
    """Example CNC milling workflow"""
    
    print("CNC Workflow Example")
    print("=" * 50)
    
    async with MoonrakerCNC() as cnc:
        try:
            # 1. Initialize machine
            print("Step 1: Initializing machine...")
            await cnc.execute_gcode("G28")  # Home all axes
            await cnc.set_coordinate_system("G54")  # Set work coordinate system
            await cnc.execute_gcode("G90")  # Absolute positioning
            await cnc.execute_gcode("G21")  # Metric units
            print("✓ Machine initialized")
            
            # 2. Tool setup
            print("\\nStep 2: Setting up tools...")
            await cnc.change_tool(1)  # Select tool 1 (e.g., end mill)
            tool_status = await cnc.get_current_tool()
            print(f"✓ Current tool: {tool_status['current_tool']}")
            
            # 3. Spindle startup
            print("\\nStep 3: Starting spindle...")
            await cnc.start_spindle(speed=1500, direction="CW")
            spindle_status = await cnc.get_spindle_status()
            print(f"✓ Spindle running at {spindle_status['spindle_speed']} RPM {spindle_status['spindle_direction']}")
            
            # 4. Enable coolant
            print("\\nStep 4: Enabling coolant...")
            await cnc.coolant_flood_on()
            coolant_status = await cnc.get_coolant_status()
            print(f"✓ Coolant status: flood={coolant_status['flood']}, mist={coolant_status['mist']}")
            
            # 5. Workpiece probing (optional)
            print("\\nStep 5: Probing workpiece...")
            await cnc.execute_gcode("G0 X5 Y5")  # Move to probe position
            await cnc.probe(z=-20, feed_rate=10)  # Probe down to find surface
            print("✓ Workpiece probed")
            
            # 6. Execute milling operations
            print("\\nStep 6: Executing milling operations...")
            
            # Simple pocket milling example
            milling_gcode = '''
            G0 Z5          ; Raise to safe height
            G0 X10 Y10     ; Move to start position
            G1 Z-2 F100    ; Plunge into material
            G1 X20 Y10 F200 ; Cut to end of pocket
            G1 X20 Y20     ; Cut side
            G1 X10 Y20     ; Cut back
            G1 X10 Y10     ; Complete pocket
            G0 Z5          ; Retract
            '''
            
            for line in milling_gcode.strip().split('\\n'):
                line = line.strip()
                if line and not line.startswith(';'):
                    await cnc.execute_gcode(line)
                    await asyncio.sleep(0.1)  # Small delay between commands
            
            print("✓ Milling operations completed")
            
            # 7. Tool change for finishing operation
            print("\\nStep 7: Changing to finishing tool...")
            await cnc.change_tool(2)  # Select tool 2 (e.g., smaller end mill)
            print("✓ Tool changed for finishing")
            
            # 8. Finishing operations (example)
            print("\\nStep 8: Finishing operations...")
            await cnc.execute_gcode("G1 Z-1 F50")  # Light finishing pass
            await cnc.execute_gcode("G1 X20 Y10 F100")
            await cnc.execute_gcode("G0 Z5")
            print("✓ Finishing completed")
            
            # 9. Shutdown sequence
            print("\\nStep 9: Shutdown sequence...")
            await cnc.stop_spindle()
            await cnc.coolant_off()
            await cnc.execute_gcode("G0 Z50")  # Raise Z to safe height
            await cnc.execute_gcode("G0 X0 Y0")  # Return to origin
            print("✓ Machine safely shutdown")
            
            print("\\n" + "=" * 50)
            print("✓ CNC workflow completed successfully!")
            
        except Exception as e:
            print(f"\\n✗ Error during workflow: {e}")
            print("Executing emergency stop...")
            try:
                await cnc.emergency_stop()
                await cnc.stop_spindle()
                await cnc.coolant_off()
            except:
                pass
            print("✓ Emergency procedures executed")


async def status_monitoring_example():
    """Example of monitoring CNC machine status"""
    
    print("\\nCNC Status Monitoring Example")
    print("=" * 50)
    
    async with MoonrakerCNC() as cnc:
        try:
            # Get all status information
            spindle_status = await cnc.get_spindle_status()
            coolant_status = await cnc.get_coolant_status()
            tool_status = await cnc.get_current_tool()
            coord_status = await cnc.get_coordinate_system()
            
            print("Current Machine Status:")
            print(f"  Spindle: {'ON' if spindle_status['spindle_running'] else 'OFF'}")
            if spindle_status['spindle_running']:
                print(f"    Speed: {spindle_status['spindle_speed']} RPM")
                print(f"    Direction: {spindle_status['spindle_direction']}")
            
            print(f"  Coolant:")
            print(f"    Flood: {'ON' if coolant_status['flood'] else 'OFF'}")
            print(f"    Mist: {'ON' if coolant_status['mist'] else 'OFF'}")
            
            print(f"  Current Tool: T{tool_status['current_tool']}")
            print(f"  Coordinate System: {coord_status['coordinate_system']}")
            
        except Exception as e:
            print(f"Error getting status: {e}")


async def main():
    """Main function to run examples"""
    print("Moonraker CNC API Examples")
    print("=" * 60)
    
    # Note: These examples assume Moonraker is running on localhost:7125
    # In a real environment, you would check connection first
    
    print("Example 1: Complete CNC Workflow")
    await cnc_workflow_example()
    
    print("\\n\\nExample 2: Status Monitoring")
    await status_monitoring_example()
    
    print("\\n" + "=" * 60)
    print("Examples completed!")
    print("\\nNote: These examples require a running Moonraker instance")
    print("with CNC component enabled and a properly configured CNC machine.")


if __name__ == "__main__":
    asyncio.run(main())