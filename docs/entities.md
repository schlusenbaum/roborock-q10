# Entities

The integration adds Q10-specific entities to the existing Roborock device.

Depending on the supported features of the vacuum, these can include the following entities.

## Fan Level

A select entity for choosing the vacuum's suction power.

Options (option value in brackets, e.g. for `select.select_option` in automations): Quiet (`quiet`), Balanced (`balanced`), Turbo (`turbo`), Max (`max`), Max+ (`max_plus`). The old values `Leise`, `Normal`, `Turbo`, `Max` and `Max+` are still accepted.

## Water Flow

A select entity for choosing the water flow used during mopping.

## Cleaning Route

A select entity named **Cleaning Route**.

It controls the Q10-specific cleaning route through the corresponding Roborock command. Options, named as in the Roborock app: Light (`daily`), Balanced (`fast`), Deep (`fine`).

## Room Selection

Room selection is handled through the integration's services and map data.

The selected rooms are stored temporarily by Home Assistant and can be used by the room cleaning service.

## Map Information

The integration maintains information about known maps and the rooms contained in those maps.

This information is used internally and can also be retrieved through the WebSocket API.

## Map Refresh

### Refresh Map (button)

Asks the robot for its current map.

> **Note:** Since Home Assistant 2026.10 (python-roborock 7.12) a docked Q10 usually answers this request with status values only, **not** with a map. The map arrives reliably during a cleaning run or when the map screen in the Roborock app is opened.

### Automatic Map Refresh (switch)

When on, requests a map refresh every 15 minutes. The state is restored after a restart.

Disabled by default on new installations, because a docked robot usually ignores the request (see **Refresh Map**).
