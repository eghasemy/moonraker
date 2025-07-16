# CNC Features for Moonraker

This repository includes comprehensive CNC (Computer Numerical Control) support for Moonraker that interfaces with Klipper's CNC extras, enabling the use of Klipper firmware for CNC operations like milling, routing, engraving, and laser cutting.

## Overview

The Moonraker CNC component provides HTTP API endpoints that interface with Klipper's CNC extras to support:

- **Spindle Control**: Start, stop, and control spindle speed and direction via Klipper's `[spindle]` extra
- **Coolant Management**: Control mist and flood coolant systems via Klipper's `[coolant]` extra
- **Tool Management**: Automatic tool changing (ATC) support via Klipper's `[tool_change]` extra
- **Coordinate Systems**: Work with multiple coordinate systems (G54-G59) via Klipper's `[work_coordinate_systems]` extra
- **Probing Operations**: Workpiece and tool length probing via Klipper's `[cnc_probing]` extra
- **Feed Hold/Pause**: Program pause and resume via Klipper's `[feed_hold]` extra
- **Canned Cycles**: Drilling cycles (G81/G82/G83) via Klipper's `[canned_cycles]` extra
- **Handwheel Control**: Manual jog control via Klipper's `[handwheel]` extra (optional)
- **Multi-Axis Support**: Rotary A/B axes via Klipper's `[multi_axis]` extra (optional)

## Prerequisites

**IMPORTANT**: This Moonraker CNC component requires Klipper with CNC extras configured. You must install and configure the Klipper CNC extras before using these Moonraker features.

### Required Klipper Extras

Configure these sections in your Klipper `printer.cfg`:

- `[spindle]` - For M3/M4/M5 spindle control with PWM speed control
- `[coolant]` - For M7/M8/M9 coolant control with GPIO outputs  
- `[tool_change]` - For T-command tool changes with macro support
- `[cnc_probing]` - For G38.x probing operations with touch probe
- `[work_coordinate_systems]` - For G54-G59 coordinate system support
- `[feed_hold]` - For M0/M1 pause/resume with safe retract
- `[canned_cycles]` - For G81/G82/G83 drilling cycle support

### Optional Klipper Extras

- `[handwheel]` - For manual jog wheel control with encoder support
- `[multi_axis]` - For A/B rotary axis support with acceleration limiting

See the Klipper CNC documentation for detailed configuration examples.

## Quick Start

### 1. Configure Klipper CNC Extras

First, configure the required Klipper extras in your `printer.cfg`. Here's a basic example:

```ini
# Basic stepper configuration (required)
[stepper_x]
# ... your stepper configuration

[stepper_y] 
# ... your stepper configuration

[stepper_z]
# ... your stepper configuration

# CNC-specific extras
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
# Automatically enables G54-G59

[feed_hold]
retract_length: 1.0
lift_z: 5.0

[canned_cycles]
default_feed_rate: 200
```

### 2. Enable Moonraker CNC Component

Add the following section to your `moonraker.conf`:

```ini
[cnc]
# This section enables CNC API endpoints that interface with Klipper extras
# No additional configuration needed - all functionality comes from Klipper
```

### 3. Test the API

Start your spindle:
```bash
curl -X POST "http://localhost:7125/printer/cnc/spindle/start" -d "speed=1500&direction=CW"
```

Check spindle status:
```bash
curl "http://localhost:7125/printer/cnc/spindle/status"
```

Stop the spindle:
```bash
curl -X POST "http://localhost:7125/printer/cnc/spindle/stop"
```

## API Reference

All endpoints interface with the corresponding Klipper extras and return real-time status information.

### Spindle Control (requires `[spindle]` in Klipper)

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/spindle/start` | POST | `speed` (int), `direction` (str) | Start spindle via M3/M4 |
| `/printer/cnc/spindle/stop` | POST | None | Stop spindle via M5 |
| `/printer/cnc/spindle/status` | GET | None | Get real-time spindle status |

### Coolant Control (requires `[coolant]` in Klipper)

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/coolant/mist` | POST | None | Turn on mist coolant via M7 |
| `/printer/cnc/coolant/flood` | POST | None | Turn on flood coolant via M8 |
| `/printer/cnc/coolant/off` | POST | None | Turn off all coolant via M9 |
| `/printer/cnc/coolant/status` | GET | None | Get real-time coolant status |

### Tool Management (requires `[tool_change]` in Klipper)

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/tool/change` | POST | `tool` (int) | Change to specified tool via T-command |
| `/printer/cnc/tool/status` | GET | None | Get current tool and configuration |

### Coordinate Systems (requires `[work_coordinate_systems]` in Klipper)

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/coordinate_system` | POST | `system` (str) | Set coordinate system (G54-G59) |
| `/printer/cnc/coordinate_system` | GET | None | Get current coordinate system and offsets |

### Probing (requires `[cnc_probing]` in Klipper)

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/probe` | POST | `x`, `y`, `z`, `feed_rate` | Execute G38.2 probe operation |

### Feed Hold and Pause (requires `[feed_hold]` in Klipper)

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/feed_hold` | POST | None | Execute immediate feed hold |
| `/printer/cnc/cycle_start` | POST | None | Resume from feed hold/pause |
| `/printer/cnc/pause_status` | GET | None | Get pause status |

### Canned Cycles (requires `[canned_cycles]` in Klipper)

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/drilling_cycle` | POST | `type`, `x`, `y`, `z`, `r`, `f`, `p`, `q` | Execute drilling cycle |
| `/printer/cnc/cancel_cycle` | POST | None | Cancel active canned cycle |

### Handwheel Control (requires `[handwheel]` in Klipper)

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/handwheel/enable` | POST | None | Enable handwheel control |
| `/printer/cnc/handwheel/disable` | POST | None | Disable handwheel control |
| `/printer/cnc/handwheel/jog` | POST | `axis`, `distance` | Manual jog command |
| `/printer/cnc/handwheel/status` | GET | None | Get handwheel status |

### Multi-Axis Support (requires `[multi_axis]` in Klipper)

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/multi_axis/status` | GET | None | Get rotary axis configuration |
| `/printer/cnc/multi_axis/home` | POST | `axis` | Home A or B rotary axis |

### G-code Execution

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/gcode/script` | POST | `script` (str) | Execute arbitrary G-code commands |
| `/printer/cnc/emergency_stop` | POST | None | Emergency stop all operations |

## Examples

See the `examples/` directory for complete workflow examples:

- `cnc_workflow_example.py` - Complete CNC milling workflow
- Python client library for easy integration

## Supported G-codes

The CNC features work with standard G-codes implemented by Klipper CNC extras:

### Motion Commands (handled by Klipper core)
- `G0` - Rapid positioning
- `G1` - Linear interpolation  
- `G2` - Clockwise arc
- `G3` - Counter-clockwise arc
- `G4` - Dwell/pause

### Coordinate Systems (via `[work_coordinate_systems]`)
- `G54`-`G59` - Work coordinate systems
- `G92` - Set position
- `G53` - Machine coordinate moves
- `G10 L2` - Set coordinate system offsets

### Spindle Control (via `[spindle]`)
- `M3` - Spindle on clockwise
- `M4` - Spindle on counter-clockwise
- `M5` - Spindle stop

### Coolant Control (via `[coolant]`)
- `M7` - Mist coolant on
- `M8` - Flood coolant on
- `M9` - All coolant off

### Tool Changes (via `[tool_change]`)
- `T0`-`T99` - Tool selection commands

### Probing (via `[cnc_probing]`)
- `G38.2` - Probe toward workpiece (error if no contact)
- `G38.3` - Probe toward workpiece (no error)
- `G38.4` - Probe away from workpiece (error if contact remains)
- `G38.5` - Probe away from workpiece (no error)

### Feed Hold/Pause (via `[feed_hold]`)
- `M0` - Program stop
- `M1` - Optional stop
- `FEED_HOLD` - Immediate motion stop
- `CYCLE_START` - Resume operation

### Canned Cycles (via `[canned_cycles]`)
- `G81` - Simple drilling cycle
- `G82` - Drilling with dwell
- `G83` - Peck drilling cycle
- `G80` - Cancel canned cycle
- `G98/G99` - Retract mode control

## Architecture

This Moonraker CNC implementation uses a clean separation of responsibilities:

**Klipper CNC Extras** (Firmware Layer):
- Real-time hardware control
- G-code command interpretation
- Motion planning and execution
- Safety systems and emergency stops
- State management and status reporting

**Moonraker CNC Component** (API Layer):
- HTTP API endpoints for remote control
- Status aggregation from Klipper objects
- WebSocket notifications for real-time updates
- Integration with web interfaces
- Higher-level workflow management

This architecture ensures that the actual CNC functionality is handled by the real-time firmware (Klipper), while Moonraker provides a convenient API interface for control and monitoring.

## Hardware Requirements

To use CNC features with Klipper/Moonraker:

1. **Control Board**: Any Klipper-compatible board
2. **Stepper Motors**: For X, Y, Z axes (and optional A/B rotary)
3. **Spindle**: With speed control (PWM/VFD) and enable/direction pins
4. **Coolant System**: Mist and/or flood coolant pumps with control relays
5. **Probe**: Touch probe for workpiece measurement
6. **Safety**: Emergency stop button and limit switches (highly recommended)

## Safety Features

- Parameter validation on all inputs
- Emergency stop capability via Klipper
- Automatic spindle stop on errors
- Coolant safety controls
- Tool number validation
- Real-time status monitoring from Klipper

## Integration

The CNC features work with popular CNC software:

- **FluidNC WebUI** - Web-based CNC interface
- **CNC.js** - Universal CNC platform
- **bCNC** - G-code sender
- **Universal G-code Sender (UGS)**
- **LinuxCNC** - Compatible via standard G-code
- **CAM software** - Any software generating standard G-code

## Development

### Running Tests

```bash
cd moonraker
python -m pytest tests/test_cnc.py -v
```

### Validation

```bash
python scripts/validate_cnc.py
```

## Contributing

When contributing to CNC features:

1. Follow existing code patterns
2. Add tests for new functionality  
3. Update documentation
4. Ensure Klipper integration compatibility
5. Test with actual CNC hardware when possible

## Acknowledgments

This CNC implementation interfaces with Klipper CNC extras and draws inspiration from:

- **Klipper CNC Extras** - The foundation for CNC functionality
- **KCNC** by vladbabii - Klipper CNC macro package
- **@eghasemy** repositories - ATC macros and CNC integration
- **CNC community** - G-code standards and best practices

## License

This code is licensed under the GNU GPLv3 license, same as Moonraker.

## Support

For support with CNC features:

1. Check the Klipper CNC extras documentation first
2. Review this documentation in `docs/cnc_support.md`
3. Review example configurations in `docs/moonraker-cnc.conf`
4. Run the validation script to check your setup
5. Test with the example workflow in `examples/`

---

**Warning**: CNC machines can be dangerous. Always follow proper safety procedures, use emergency stops, and test thoroughly before production use.