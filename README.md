# Roborock Q10

Home Assistant Custom Integration for Roborock Q10 devices.

## Features

- Q10 map room detection
- Room IDs and room names
- WebSocket API for room information
- Map update events
- Support for Q10-specific map handling

## Installation

Install via HACS as a custom repository:

1. Open HACS
2. Open Integrations
3. Add this repository as a custom repository
4. Select `Integration`
5. Install **Roborock Q10**
6. Restart Home Assistant

## Requirements

The official Home Assistant Roborock integration must also be installed and configured.

This integration extends the Q10 functionality provided by the official Roborock integration.

## Room IDs

The integration reads the room IDs directly from the Q10 map.

Example:

- `1` – Corridor
- `3` – Kitchen
- `4` – Entrance Hall
- `5` – Bad
- `6` – Wohn/Esszimmer

## License

MIT
