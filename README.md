# Roborock Q10

Home Assistant custom integration for Roborock Q10 devices.

This integration extends Home Assistant's official Roborock integration with Q10-specific functionality for maps, rooms, and cleaning controls.

> **Important:** This integration does not replace the official Home Assistant Roborock integration. It uses an existing Roborock vacuum entity and adds additional entities and services.

## Features

- Read rooms directly from the Q10 map
- Provide room IDs and room names
- Catalog known Q10 maps
- Refresh the map manually
- Automatically refresh map information every 15 minutes
- Select rooms for cleaning
- Clean selected rooms
- Clean rooms by ID or name using services
- Control fan level
- Control water flow
- Select the cleaning route
- Provide diagnostics and WebSocket functionality

## Requirements

- Home Assistant
- The official Home Assistant Roborock integration
- A Roborock Q10 configured through the official integration

## Documentation

### English

- [Installation](docs/installation.md)
- [Configuration](docs/configuration.md)
- [Entities](docs/entities.md)
- [Rooms and Maps](docs/rooms-and-maps.md)
- [Services](docs/services.md)
- [Automations](docs/automations.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Development](docs/development.md)

### Deutsch
🇩🇪 [Deutsche Dokumentation](docs/de/README.md)

- [Installation](docs/de/installation.md)
- [Konfiguration](docs/de/configuration.md)
- [Entities](docs/de/entities.md)
- [Räume und Karten](docs/de/rooms-and-maps.md)
- [Services](docs/de/services.md)
- [Automationen](docs/de/automations.md)
- [Fehlerbehebung](docs/de/troubleshooting.md)
- [Entwicklung](docs/de/development.md)

## Technical Overview

The integration builds on the vacuum entity provided by Home Assistant's official Roborock integration.

It adds Q10-specific functionality without replacing or duplicating the existing Roborock integration.
