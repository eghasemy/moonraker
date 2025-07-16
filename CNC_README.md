# CNC Features for Moonraker

This repository includes comprehensive CNC (Computer Numerical Control) support for Moonraker, enabling the use of Klipper firmware for CNC operations like milling, routing, engraving, and laser cutting.

## Overview

The CNC features extend Moonraker's capabilities to support:

- **Spindle Control**: Start, stop, and control spindle speed and direction
- **Coolant Management**: Control mist and flood coolant systems
- **Tool Management**: Automatic tool changing (ATC) support
- **Coordinate Systems**: Work with multiple coordinate systems (G54-G59)
- **Probing Operations**: Workpiece and tool length probing
- **Safety Features**: Emergency stop and error handling

## Quick Start

### 1. Enable CNC Features

Add the following section to your `moonraker.conf`:

```ini
[cnc]
# This section enables CNC API endpoints
```

### 2. Configure Klipper for CNC

Your Klipper configuration should include CNC-specific outputs:

```ini
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

### Spindle Control

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/spindle/start` | POST | `speed` (int), `direction` (str) | Start spindle |
| `/printer/cnc/spindle/stop` | POST | None | Stop spindle |
| `/printer/cnc/spindle/status` | GET | None | Get spindle status |

### Coolant Control

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/coolant/mist` | POST | None | Turn on mist coolant |
| `/printer/cnc/coolant/flood` | POST | None | Turn on flood coolant |
| `/printer/cnc/coolant/off` | POST | None | Turn off all coolant |
| `/printer/cnc/coolant/status` | GET | None | Get coolant status |

### Tool Management

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/tool/change` | POST | `tool` (int) | Change to specified tool |
| `/printer/cnc/tool/status` | GET | None | Get current tool number |

### Coordinate Systems

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/coordinate_system` | POST | `system` (str) | Set coordinate system (G54-G59) |
| `/printer/cnc/coordinate_system` | GET | None | Get current coordinate system |

### Probing

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/cnc/probe` | POST | `x`, `y`, `z`, `feed_rate` | Execute probe operation |

### G-code Execution

| Endpoint | Method | Parameters | Description |
|----------|--------|------------|-------------|
| `/printer/gcode/script` | POST | `script` (str) | Execute G-code commands |
| `/printer/cnc/emergency_stop` | POST | None | Emergency stop all operations |

## Examples

See the `examples/` directory for complete workflow examples:

- `cnc_workflow_example.py` - Complete CNC milling workflow
- Python client library for easy integration

## Supported G-codes

The CNC features work with standard G-codes through Klipper:

### Motion Commands
- `G0` - Rapid positioning
- `G1` - Linear interpolation  
- `G2` - Clockwise arc
- `G3` - Counter-clockwise arc
- `G4` - Dwell/pause

### Coordinate Systems
- `G54`-`G59` - Work coordinate systems
- `G90` - Absolute positioning
- `G91` - Incremental positioning

### Spindle Control
- `M3` - Spindle on clockwise
- `M4` - Spindle on counter-clockwise
- `M5` - Spindle stop

### Coolant Control
- `M7` - Mist coolant on
- `M8` - Flood coolant on
- `M9` - All coolant off

### Probing
- `G38.2` - Straight probe toward workpiece

## Hardware Requirements

To use CNC features:

1. **Control Board**: Any Klipper-compatible board
2. **Stepper Motors**: For X, Y, Z axes
3. **Spindle**: With speed control (0-10V or PWM)
4. **Coolant System**: Mist and/or flood coolant pumps
5. **Probe**: Touch probe for workpiece measurement
6. **Safety**: Emergency stop button (highly recommended)

## Safety Features

- Input validation for all parameters
- Emergency stop functionality
- Automatic spindle stop on errors
- Coolant safety controls
- Tool number validation

## Integration

The CNC features are designed to work with:

- **FluidNC WebUI** - Web-based CNC interface
- **CNC.js** - Universal CNC platform
- **bCNC** - G-code sender
- **Universal G-code Sender (UGS)**
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
4. Test with actual CNC hardware when possible

## Acknowledgments

This CNC implementation draws inspiration from:

- **KCNC** by vladbabii - Klipper CNC macro package
- **@eghasemy** repositories - ATC macros and FluidNC integration
- **CNC community** - G-code standards and best practices

## License

This code is licensed under the GNU GPLv3 license, same as Moonraker.

## Support

For support with CNC features:

1. Check the documentation in `docs/cnc_support.md`
2. Review example configurations in `docs/moonraker-cnc.conf`
3. Run the validation script to check your setup
4. Test with the example workflow in `examples/`

---

**Warning**: CNC machines can be dangerous. Always follow proper safety procedures, use emergency stops, and test thoroughly before production use.