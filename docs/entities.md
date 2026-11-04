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

## Map Refresh

### Refresh Map (button)

Asks the robot for its current map.

> **Note:** Since Home Assistant 2026.10 (python-roborock 7.12) a docked Q10 usually answers this request with status values only, **not** with a map. The map arrives reliably during a cleaning run or when the map screen in the Roborock app is opened. The **Legacy map request (experimental)** switch works around this, see below.

### Automatic Map Refresh (switch)

When on, requests a map refresh every 15 minutes. The state is restored after a restart.

Disabled by default on new installations, because a docked robot usually ignores the request (see **Refresh Map**). It is mainly useful together with the experimental switch.

### Legacy map request (experimental) (switch)

Off by default. When on, **Refresh Map** and **Automatic Map Refresh** additionally request the map the way python-roborock did up to Home Assistant 2026.9 (`dpMultiMap op:get` with the saved map's ID). This makes the robot push its map even while docked.

> **Warning:** python-roborock removed this method because some Q10 firmware treats it as a cleaning/relocation command. **The robot may start moving.** Test it while you are at home first, and only combine it with Automatic Map Refresh if this does not happen on your robot.

