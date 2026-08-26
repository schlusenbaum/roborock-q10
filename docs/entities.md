# Entities

The integration adds Q10-specific entities to the existing Roborock device.

Depending on the supported features of the vacuum, these can include the following entities.

## Fan Level

A select entity for choosing the vacuum's suction power.

The available options are based on the Q10 fan levels supported by the underlying Roborock API.

## Water Flow

A select entity for choosing the water flow used during mopping.

## Cleaning Route

A select entity named **Cleaning Route**.

It controls the Q10-specific cleaning route through the corresponding Roborock command.

## Room Selection

Room selection is handled through the integration's services and map data.

The selected rooms are stored temporarily by Home Assistant and can be used by the room cleaning service.

## Map Information

The integration maintains information about known maps and the rooms contained in those maps.

This information is used internally and can also be retrieved through the WebSocket API.
