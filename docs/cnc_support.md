# CNC Support in Moonraker

Moonraker now includes comprehensive CNC (Computer Numerical Control) machine support that interfaces with Klipper's CNC extras, enabling the use of Klipper firmware for CNC operations like milling, routing, laser cutting, and more.

## Prerequisites

This Moonraker CNC component requires Klipper with the CNC extras modules. The following Klipper extras should be configured in your `printer.cfg`:

- `[spindle]` - For M3/M4/M5 spindle control
- `[coolant]` - For M7/M8/M9 coolant control  
- `[tool_change]` - For T-command tool changes
- `[cnc_probing]` - For G38.x probing operations
- `[work_coordinate_systems]` - For G54-G59 coordinate systems
- `[feed_hold]` - For M0/M1 pause/resume functionality
- `[canned_cycles]` - For G81/G82/G83 drilling cycles
- `[handwheel]` - For manual jog wheel control (optional)
- `[multi_axis]` - For A/B rotary axes (optional)

See the Klipper CNC documentation for detailed configuration of these extras.

## Configuration

To enable CNC features in Moonraker, add a `[cnc]` section to your `moonraker.conf`:

```ini
[cnc]
# Enable CNC mode - this section presence enables CNC API endpoints
# The actual CNC functionality is provided by Klipper extras
```

## API Endpoints

All API endpoints interface with the corresponding Klipper extras and return real-time status from Klipper.

### Spindle Control

Control spindle operation using the Klipper `[spindle]` extra.

#### Start Spindle
`POST /printer/cnc/spindle/start`

Parameters:
- `speed` (int, optional): Spindle speed in RPM (default: 1000)
- `direction` (string, optional): Rotation direction "CW" or "CCW" (default: "CW")

Executes M3 (CW) or M4 (CCW) commands and returns current status from Klipper spindle extra.

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/spindle/start" \
     -d "speed=1500&direction=CW"
```

#### Stop Spindle
`POST /printer/cnc/spindle/stop`

Executes M5 command and returns current status from Klipper spindle extra.

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/spindle/stop"
```

#### Get Spindle Status
`GET /printer/cnc/spindle/status`

Returns real-time status from Klipper spindle extra:
```json
{
  "spindle_running": true,
  "spindle_speed": 1500,
  "spindle_direction": "CW"
}
```

### Coolant Control

Control coolant systems using the Klipper `[coolant]` extra.

#### Mist Coolant On
`POST /printer/cnc/coolant/mist`

Executes M7 command and returns current status from Klipper coolant extra.

#### Flood Coolant On
`POST /printer/cnc/coolant/flood`

Executes M8 command and returns current status from Klipper coolant extra.

#### All Coolant Off
`POST /printer/cnc/coolant/off`

Executes M9 command and returns current status from Klipper coolant extra.

#### Get Coolant Status
`GET /printer/cnc/coolant/status`

Returns real-time status from Klipper coolant extra:
```json
{
  "mist": false,
  "flood": true
}
```

### Tool Management

Handle tool changes using the Klipper `[tool_change]` extra.

#### Change Tool
`POST /printer/cnc/tool/change`

Parameters:
- `tool` (int, required): Tool number to change to

Executes T-command and returns current status from Klipper tool_change extra.

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/tool/change" \
     -d "tool=5"
```

#### Get Current Tool
`GET /printer/cnc/tool/status`

Returns real-time status from Klipper tool_change extra:
```json
{
  "current_tool": 5,
  "max_tool": 99
}
```

### Coordinate Systems

Manage work coordinate systems using the Klipper `[work_coordinate_systems]` extra.

#### Set Coordinate System
`POST /printer/cnc/coordinate_system`

Parameters:
- `system` (string, required): Coordinate system ("G54", "G55", "G56", "G57", "G58", "G59")

Executes G-code command and returns current status from Klipper work_coordinate_systems extra.

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/coordinate_system" \
     -d "system=G55"
```

#### Get Current Coordinate System
`GET /printer/cnc/coordinate_system`

Returns real-time status from Klipper work_coordinate_systems extra:
```json
{
  "coordinate_system": "G55",
  "coordinate_systems": {
    "54": [0.0, 0.0, 0.0, 0.0],
    "55": [10.0, 10.0, 5.0, 0.0]
  }
}
```

### Probing Operations

Execute probing operations using the Klipper `[cnc_probing]` extra.

#### Execute Probe
`POST /printer/cnc/probe`

Parameters:
- `x` (float, optional): Target X position
- `y` (float, optional): Target Y position
- `z` (float, optional): Target Z position
- `feed_rate` (float, optional): Probing feed rate in mm/s (default: 5.0)

Executes G38.2 command and returns probe results from Klipper cnc_probing extra.

Example:
```bash
curl -X POST "http://localhost:7125/printer/cnc/probe" \
     -d "x=10.0&y=20.0&z=-5.0&feed_rate=8.0"
```

### Feed Hold and Pause

Control program pauses using the Klipper `[feed_hold]` extra.

#### Feed Hold
`POST /printer/cnc/feed_hold`

Executes immediate feed hold and returns status from Klipper feed_hold extra.

#### Cycle Start
`POST /printer/cnc/cycle_start`

Resumes from feed hold or pause and returns status from Klipper feed_hold extra.

#### Get Pause Status
`GET /printer/cnc/pause_status`

Returns real-time pause status from Klipper feed_hold extra:
```json
{
  "is_paused": false,
  "pause_position": null,
  "feed_hold_pin_state": null
}
```

### Canned Drilling Cycles

Execute drilling cycles using the Klipper `[canned_cycles]` extra.

#### Execute Drilling Cycle
`POST /printer/cnc/drilling_cycle`

Parameters:
- `type` (string, optional): Cycle type "G81", "G82", "G83" (default: "G81")
- `x` (float, optional): X position
- `y` (float, optional): Y position
- `z` (float, required): Z depth
- `r` (float, required): R plane
- `f` (float, optional): Feed rate (default: 100)
- `p` (float, optional): Dwell time for G82
- `q` (float, optional): Peck depth for G83

#### Cancel Canned Cycle
`POST /printer/cnc/cancel_cycle`

Executes G80 to cancel active canned cycle.

### Handwheel Control

Manual jog control using the Klipper `[handwheel]` extra (if configured).

#### Enable Handwheel
`POST /printer/cnc/handwheel/enable`

#### Disable Handwheel
`POST /printer/cnc/handwheel/disable`

#### Manual Jog
`POST /printer/cnc/handwheel/jog`

Parameters:
- `axis` (string, required): Axis to jog "X", "Y", "Z", "A", "B", "E"
- `distance` (float, required): Distance to jog in mm

#### Get Handwheel Status
`GET /printer/cnc/handwheel/status`

Returns real-time status from Klipper handwheel extra.

### Multi-Axis Support

Rotary axis control using the Klipper `[multi_axis]` extra (if configured).

#### Get Multi-Axis Status
`GET /printer/cnc/multi_axis/status`

Returns configuration and status of rotary axes.

#### Home Rotary Axis
`POST /printer/cnc/multi_axis/home`

Parameters:
- `axis` (string, required): Rotary axis to home "A" or "B"

### General G-code Execution

#### Execute G-code Script
`POST /printer/gcode/script`

Parameters:
- `script` (string, required): G-code commands to execute

This endpoint allows execution of arbitrary G-code, including CNC-specific commands handled by Klipper extras.

Example:
```bash
curl -X POST "http://localhost:7125/printer/gcode/script" \
     -d "script=G1 X10 Y10 F100"
```

#### Emergency Stop
`POST /printer/cnc/emergency_stop`

Immediately stops all motion and spindle operation using Klipper's emergency stop mechanism.

## Klipper CNC Extras Integration

Moonraker's CNC component interfaces with the following Klipper extras:

### Required Klipper Configuration

The CNC functionality requires specific Klipper extras to be configured in your `printer.cfg`. See the Klipper CNC documentation for detailed configuration examples:

- **[spindle]** - Provides M3/M4/M5 commands with PWM speed control
- **[coolant]** - Provides M7/M8/M9 commands for mist/flood coolant
- **[tool_change]** - Provides T-commands with automated tool change sequences
- **[cnc_probing]** - Provides G38.x commands for touch probing
- **[work_coordinate_systems]** - Provides G54-G59 coordinate system support
- **[feed_hold]** - Provides M0/M1 pause/resume with safe retract
- **[canned_cycles]** - Provides G81/G82/G83 drilling cycles

Optional extras for advanced features:
- **[handwheel]** - Manual jog wheel control
- **[multi_axis]** - A/B rotary axis support

### Status Information

All API endpoints return real-time status information queried directly from the Klipper extras, ensuring consistency between the API and actual machine state.

## Integration with CNC Software

Moonraker's CNC features work with popular CNC software:

- **FluidNC** - Web-based CNC controller interface
- **CNC.js** - Web-based CNC milling controller  
- **bCNC** - GRBL CNC command sender
- **UGS (Universal Gcode Sender)** - Java-based G-code sender
- **LinuxCNC** - Real-time CNC controller (via G-code compatibility)

## Klipper vs. Moonraker Responsibilities

**Klipper Handles:**
- Real-time motion control and G-code interpretation
- Hardware interface (pins, PWM, steppers)
- CNC-specific command implementation (M3/M4/M5, G38.x, etc.)
- Safety systems and emergency stops
- State management and status reporting

**Moonraker Provides:**
- HTTP API endpoints for remote control
- WebSocket notifications for real-time updates
- Integration with web interfaces
- Higher-level workflow management
- Status aggregation from multiple Klipper objects

## Example Klipper Configuration

Here's a basic Klipper configuration with CNC extras:

```ini
[mcu]
serial: /dev/serial/by-id/your-board-id

# Basic stepper configuration
[stepper_x]
step_pin: PB13
dir_pin: !PB12
enable_pin: !PB14
microsteps: 16
rotation_distance: 40
endstop_pin: ^PC0
position_endstop: 0
position_max: 400

[stepper_y]
step_pin: PB10
dir_pin: !PB2
enable_pin: !PB11
microsteps: 16
rotation_distance: 40
endstop_pin: ^PC1
position_endstop: 0
position_max: 300

[stepper_z]
step_pin: PB0
dir_pin: PC5
enable_pin: !PB1
microsteps: 16
rotation_distance: 8
endstop_pin: ^PC2
position_endstop: 0.0
position_max: 100

# CNC-specific configuration
[spindle]
enable_pin: PA8
pwm_pin: PA9
cycle_time: 0.001
min_rpm: 100
max_rpm: 24000

[coolant]
mist_pin: PA10
flood_pin: PA11

[tool_change]
max_tool: 20
park_x: 0
park_y: 0
park_z: 25

[cnc_probing]
probe_pin: ^PC15
speed: 5
samples: 3

[work_coordinate_systems]
# Automatically enables G54-G59 support

[feed_hold]
retract_length: 1.0
lift_z: 5.0

[canned_cycles]
default_feed_rate: 200
```

## Safety Considerations

1. **Emergency Stop**: Always wire a physical emergency stop button
2. **Limit Switches**: Use endstop switches to prevent crashes  
3. **Spindle Safety**: Ensure spindle stops on emergency stop
4. **Coolant Safety**: Implement coolant overflow protection
5. **Tool Safety**: Verify tool changes before starting operations
6. **Power Safety**: Use proper relays/contactors for high-power devices