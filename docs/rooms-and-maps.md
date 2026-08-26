# Rooms and Maps

## Reading Rooms

The integration reads room information from the map data provided by the existing Roborock vacuum entity.

Each room can contain information such as:

- room ID
- room name
- original room name
- map-related pixel information

## Known Maps

The integration maintains a catalog of maps received from the Roborock API.

For each map, information such as the following can be stored:

- map ID
- width
- height
- rooms belonging to the map

## Map Update Events

When new map data is received, the integration fires a map update event.

This allows other components, dashboards, or custom cards to react to updated room and map information.

## Selected Rooms

Rooms can be selected by name.

The integration validates the requested room names against the rooms known from the current map.

The selected rooms can then be cleaned through the room cleaning service.
