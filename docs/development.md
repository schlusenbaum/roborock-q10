# Development

## Architecture

The integration is designed as an extension of Home Assistant's official Roborock integration.

It does not establish its own Roborock connection. Instead, it accesses the existing vacuum entity, its coordinator, and the underlying Roborock API.

Conceptually:

```text
Official Roborock integration
            |
            v
      Vacuum entity
            |
            v
     Q10 extension
       |    |    |
      Maps Rooms Controls
```

## Main Components

The integration contains functionality for:

- setup and config entries
- Q10-specific entities
- room discovery
- map listeners
- map catalog handling
- room selection
- room cleaning
- diagnostics
- WebSocket commands

## Room Data

Room information is obtained from:

`entity.coordinator.api.map.rooms`

The integration can refresh the API when room data is not immediately available.

## Map Listeners

A map update listener is registered for the Q10 vacuum.

When new map data is received, the integration updates its internal map catalog and fires a Home Assistant event.

## Packet Listener

The integration can also wrap the API message handler to inspect incoming Q10-specific packets.

This is used to collect additional information from map-related messages.

## Q10 Commands

Some Q10-specific functions use commands not exposed directly as high-level methods by the underlying API.

For example, the cleaning route is sent through the appropriate Roborock command and Q10 DP value.

When adding additional commands, keep the implementation isolated and document the corresponding protocol details.

## Diagnostics

The diagnostic functionality is intended to inspect available Q10 information without changing the normal behavior of the vacuum.

Diagnostic modes can be extended when investigating additional API fields or device commands.

## Development Guidelines

When modifying the integration:

1. Keep the official Roborock integration as the source of the vacuum connection.
2. Avoid duplicating functionality already provided by Home Assistant.
3. Prefer small, isolated changes.
4. Add debug logging for newly discovered Q10 behavior.
5. Test changes against a real Q10 where possible.
6. Keep user-facing documentation synchronized with implementation changes.

## Potential Upstream Contribution

The project may serve as a proof of concept for Q10-specific functionality that could eventually be contributed to the official Home Assistant Roborock integration or its underlying libraries.

For an upstream contribution, functionality should ideally be split into focused changes rather than submitting the entire custom integration as a single replacement.
