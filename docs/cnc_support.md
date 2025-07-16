# CNC Support in Moonraker

Moonraker now includes CNC (Computer Numerical Control) machine support, enabling the use of Klipper firmware for CNC operations like milling, routing, and laser cutting.

## Configuration

To enable CNC features, add a `[cnc]` section to your `moonraker.conf`:

```ini
[cnc]
# Enable CNC mode - this section presence enables CNC API endpoints
```

## API Endpoints

### Spindle Control

Control spindle operation for cutting tools.

#### Start Spindle
`POST /printer/cnc/spindle/start`

Parameters:
- `speed` (int, optional): Spindle speed in RPM (default: 1000)
- `direction` (string, optional): Rotation direction "CW" or "CCW" (default: "CW")

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/spindle/start" \
     -d "speed=1500&direction=CW"
```

#### Stop Spindle
`POST /printer/cnc/spindle/stop`

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/spindle/stop"
```

#### Get Spindle Status
`GET /printer/cnc/spindle/status`

Returns:
```json
{
  "spindle_running": true,
  "spindle_speed": 1500,
  "spindle_direction": "CW"
}
```

### Coolant Control

Control coolant systems for chip removal and cooling.

#### Mist Coolant On
`POST /printer/cnc/coolant/mist`

Executes `M7` gcode command.

#### Flood Coolant On
`POST /printer/cnc/coolant/flood`

Executes `M8` gcode command.

#### All Coolant Off
`POST /printer/cnc/coolant/off`

Executes `M9` gcode command to turn off all coolant.

#### Get Coolant Status
`GET /printer/cnc/coolant/status`

Returns:
```json
{
  "mist": false,
  "flood": true
}
```

### Tool Management

Handle tool changes for automatic tool changers (ATC).

#### Change Tool
`POST /printer/cnc/tool/change`

Parameters:
- `tool` (int, required): Tool number to change to

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/tool/change" \
     -d "tool=5"
```

#### Get Current Tool
`GET /printer/cnc/tool/status`

Returns:
```json
{
  "current_tool": 5
}
```

### Coordinate Systems

Manage work coordinate systems (G54-G59).

#### Set Coordinate System
`POST /printer/cnc/coordinate_system`

Parameters:
- `system` (string, required): Coordinate system ("G54", "G55", "G56", "G57", "G58", "G59")

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/coordinate_system" \
     -d "system=G55"
```

#### Get Current Coordinate System
`GET /printer/cnc/coordinate_system`

Returns:
```json
{
  "coordinate_system": "G55"
}
```

### Probing Operations

Execute probing operations for workpiece measurement and tool length detection.

#### Execute Probe
`POST /printer/cnc/probe`

Parameters:
- `x` (float, optional): Target X position
- `y` (float, optional): Target Y position
- `z` (float, optional): Target Z position
- `feed_rate` (float, optional): Probing feed rate (default: 5.0)

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/probe" \
     -d "x=10.0&y=20.0&z=-5.0&feed_rate=8.0"
```

### General G-code Execution

#### Execute G-code Script
`POST /printer/gcode/script`

Parameters:
- `script` (string, required): G-code commands to execute

Example:
```bash
curl -X POST "http://localhost:7125/printer/gcode/script" \
     -d "script=G1 X10 Y10 F100"
```

#### Emergency Stop
`POST /printer/cnc/emergency_stop`

Immediately stops all motion and spindle operation.

## CNC-Specific G-codes Supported

The following G-codes are commonly used in CNC operations and are supported through Klipper:

### Motion Commands
- `G0` - Rapid positioning
- `G1` - Linear interpolation
- `G2` - Clockwise circular interpolation
- `G3` - Counter-clockwise circular interpolation
- `G4` - Dwell/pause

### Coordinate Systems
- `G54` - Work coordinate system 1
- `G55` - Work coordinate system 2
- `G56` - Work coordinate system 3
- `G57` - Work coordinate system 4
- `G58` - Work coordinate system 5
- `G59` - Work coordinate system 6

### Machine Control
- `G28` - Return to home position
- `G30` - Return to secondary home position
- `G90` - Absolute positioning mode
- `G91` - Incremental positioning mode

### Spindle Control
- `M3` - Spindle on clockwise
- `M4` - Spindle on counter-clockwise
- `M5` - Spindle stop

### Coolant Control
- `M7` - Mist coolant on
- `M8` - Flood coolant on
- `M9` - All coolant off

### Tool Control
- `T{n}` - Select tool number n

### Probing
- `G38.2` - Straight probe toward workpiece, stop on contact

## Integration with CNC Software

Moonraker's CNC features are designed to work with:

- **FluidNC** - Web-based CNC controller interface
- **CNC.js** - Web-based CNC milling controller
- **bCNC** - GRBL CNC command sender
- **UGS (Universal Gcode Sender)** - Java-based G-code sender

## Hardware Requirements

To use CNC features with Klipper/Moonraker:

1. **Control Board**: Any Klipper-compatible board (SKR, RAMPS, etc.)
2. **Stepper Drivers**: For X, Y, Z axes
3. **Spindle Control**: Output pin for spindle speed control (PWM)
4. **Coolant Control**: Output pins for mist/flood coolant
5. **Probe Input**: Input pin for probe contact detection
6. **Emergency Stop**: Physical e-stop switch recommended

## Example Klipper Configuration

```ini
[mcu]
serial: /dev/serial/by-id/your-board-id

[stepper_x]
step_pin: PB13
dir_pin: !PB12
enable_pin: !PB14
microsteps: 16
rotation_distance: 40
endstop_pin: ^PC0
position_endstop: 0
position_max: 235

[stepper_y]
step_pin: PB10
dir_pin: !PB2
enable_pin: !PB11
microsteps: 16
rotation_distance: 40
endstop_pin: ^PC1
position_endstop: 0
position_max: 235

[stepper_z]
step_pin: PB0
dir_pin: PC5
enable_pin: !PB1
microsteps: 16
rotation_distance: 8
endstop_pin: ^PC2
position_endstop: 0.0
position_max: 250

[output_pin spindle]
pin: PA8
pwm: true
cycle_time: 0.001
value: 0
shutdown_value: 0

[output_pin coolant_flood]
pin: PA9
value: 0
shutdown_value: 0

[output_pin coolant_mist]
pin: PA10
value: 0
shutdown_value: 0

[probe]
pin: ^PC15
x_offset: 0
y_offset: 25.0
z_offset: 1.35
```

## Safety Considerations

1. **Emergency Stop**: Always wire a physical emergency stop button
2. **Limit Switches**: Use endstop switches to prevent crashes
3. **Spindle Safety**: Ensure spindle stops on emergency stop
4. **Coolant Safety**: Implement coolant overflow protection
5. **Tool Safety**: Verify tool changes before starting operations