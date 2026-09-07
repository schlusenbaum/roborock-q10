# Roborock Q10

Home Assistant custom integration for Roborock Q10 devices.

This integration extends Home Assistant's official Roborock integration with Q10-specific functionality for maps, rooms, cleaning controls, and map orientation.

> **Important:** This integration does not replace the official Home Assistant Roborock integration. It uses an existing Roborock vacuum entity and adds additional entities and services.

## Features

- Read rooms directly from the Q10 map
- Provide room IDs and room names
- Catalog known Q10 maps
- Display the Q10 map as a Home Assistant image entity
- Configure map rotation (0°, 90°, 180°, 270°)
- Configure horizontal and vertical map mirroring
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

- **[Installation](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/installation.md)**
- **[Configuration](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/configuration.md)**
- **[Entities](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/entities.md)**
- **[Rooms and Maps](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/rooms-and-maps.md)**
- **[Services](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/services.md)**
- **[Automations](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/automations.md)**
- **[Troubleshooting](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/troubleshooting.md)**
- **[Development](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/development.md)**

### Deutsch

- **[Deutsche Dokumentation](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/README.md)**
- **[Installation](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/installation.md)**
- **[Konfiguration](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/configuration.md)**
- **[Entities](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/entities.md)**
- **[Räume und Karten](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/rooms-and-maps.md)**
- **[Services](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/services.md)**
- **[Automationen](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/automations.md)**
- **[Fehlerbehebung](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/troubleshooting.md)**
- **[Entwicklung](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/development.md)**

## Technical Overview

The integration builds on the vacuum entity provided by Home Assistant's official Roborock integration.

It adds Q10-specific functionality without replacing or duplicating the existing Roborock integration.

Map orientation is configurable per installation because the correct orientation may differ between Q10 variants or individual installations.

The integration currently provides independent controls for rotation, horizontal mirroring, and vertical mirroring. These settings are applied directly to the generated map image.
