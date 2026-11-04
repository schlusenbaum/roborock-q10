"""Helpers that work with the Q10 map API of python-roborock >= 7.12.

Since python-roborock 7.12 (Home Assistant 2026.10) the Q10
``MapContentTrait`` no longer exposes ``map_data``. The raw map is only
available as the latest ``Q10MapPacket`` (``_map_packet``), the rendered PNG
as ``image_content`` and the rooms as ``rooms``. Everything in this module
reads those attributes defensively so it keeps working if the library
changes again.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Q10 DPS code of the live-map heartbeat the Roborock app sends while the
# map screen is open (B01_Q10_DP.HEARTBEAT = ("dpHeartbeat", 110)).
_HEARTBEAT_CODE = "110"


def get_map_packet(api: Any) -> Any | None:
    """Return the latest decoded Q10 map packet, if any."""
    map_api = getattr(api, "map", None)
    if map_api is None:
        return None
    return getattr(map_api, "_map_packet", None)


def get_rooms(api: Any) -> list[Any]:
    """Return the rooms of the current map (never None)."""
    map_api = getattr(api, "map", None)
    if map_api is None:
        return []
    return list(getattr(map_api, "rooms", None) or [])


def legacy_request_enabled(hass: Any, vacuum_entity_id: str) -> bool:
    """Whether the experimental legacy map request is switched on."""
    return bool(
        hass.data.get("roborock_q10", {})
        .get("legacy_map_request", {})
        .get(vacuum_entity_id, False)
    )


MAP_ID_STORE_KEY = "roborock_q10.map_ids"


def known_map_id(hass: Any, vacuum_entity_id: str) -> str | None:
    """Last map id seen for this robot, kept across restarts."""
    return (
        hass.data.get("roborock_q10", {})
        .get("map_ids", {})
        .get(vacuum_entity_id)
    )


def remember_map_id(hass: Any, vacuum_entity_id: str, map_id: Any) -> None:
    """Store the id of a received map so the legacy request works after a restart."""
    if map_id is None:
        return

    data = hass.data.setdefault("roborock_q10", {})
    map_ids = data.setdefault("map_ids", {})
    map_id = str(map_id)

    if map_ids.get(vacuum_entity_id) == map_id:
        return

    map_ids[vacuum_entity_id] = map_id
    store = data.get("map_id_store")
    if store is not None:
        store.async_delay_save(lambda: dict(map_ids), 5)


async def request_map_legacy(api: Any, fallback_map_id: str | None = None) -> bool:
    """EXPERIMENTAL: request the map like python-roborock < 7.4 did.

    Fetches the saved-map list if needed and then sends
    ``dpMultiMap {"op": "get", "id": <map id>}``. This makes the robot push
    its full map even when docked, but python-roborock dropped it because
    some ss07 firmware treats it as a cleaning/relocation command, i.e. the
    robot may start moving. Only used when the user switches it on.
    """
    try:
        from roborock.data.b01_q10.b01_q10_code_mappings import B01_Q10_DP
    except ImportError:
        return False

    maps = getattr(api, "maps", None)
    command = getattr(api, "command", None)

    if maps is None or command is None:
        return False

    map_id = getattr(maps, "current_map_id", None)

    if map_id is None:
        # Many robots never answer the saved-map list request, but the id is
        # also part of every map packet we already received.
        packet_id = getattr(get_map_packet(api), "map_id", None)
        if packet_id is not None:
            map_id = str(packet_id)

    if map_id is None:
        # After a restart no map packet has arrived yet: use the id we
        # remembered from the last one.
        map_id = fallback_map_id

    if map_id is None:
        try:
            await maps.refresh()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Q10 legacy map request: map list failed: %s", err)
            return False

        for _ in range(20):
            await asyncio.sleep(0.25)
            map_id = getattr(maps, "current_map_id", None)
            if map_id is not None:
                break

    if map_id is None:
        _LOGGER.debug("Q10 legacy map request: no saved map id available")
        return False

    try:
        await command.send(
            B01_Q10_DP.COMMON,
            {str(B01_Q10_DP.MULTI_MAP.code): {"op": "get", "id": map_id}},
        )
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Q10 legacy map request failed: %s", err)
        return False

    _LOGGER.debug("Q10 legacy map request sent for map %s", map_id)
    return True


async def request_map(
    api: Any, legacy: bool = False, fallback_map_id: str | None = None
) -> None:
    """Ask the robot to push its current map.

    1. ``api.map.refresh()`` - read-only current-map request of the library.
    2. Live-map heartbeat ``COMMON {"110": 1}`` - what the Roborock app sends
       while its map screen is open. Some firmware only pushes the full map
       after this. Failures are logged and ignored.
    """
    if legacy:
        await request_map_legacy(api, fallback_map_id)

    map_api = getattr(api, "map", None)
    refresh = getattr(map_api, "refresh", None)

    try:
        if refresh is not None:
            await refresh()
        else:
            await api.refresh()
    except Exception as err:  # noqa: BLE001 - must never break callers
        _LOGGER.debug("Q10 map refresh request failed: %s", err)

    try:
        from roborock.data.b01_q10.b01_q10_code_mappings import B01_Q10_DP

        command = getattr(api, "command", None)
        if command is not None:
            await command.send(B01_Q10_DP.COMMON, {_HEARTBEAT_CODE: 1})
    except Exception as err:  # noqa: BLE001 - heartbeat is best effort
        _LOGGER.debug("Q10 live-map heartbeat failed: %s", err)


def room_centroids(api: Any) -> list[dict[str, Any]]:
    """Compute a label position for every room from the raw map grid.

    The grid is ``width * height`` bytes, top-down, and every cell of a room
    holds ``room.pixel_value``. The rendered map image is this grid scaled
    uniformly (no flip), so coordinates are returned in grid space together
    with ``map_width``/``map_height`` for the frontend to scale.
    """
    packet = get_map_packet(api)
    rooms = get_rooms(api)

    if packet is None or not rooms:
        return []

    width = getattr(packet, "width", 0)
    height = getattr(packet, "height", 0)
    grid = getattr(packet, "grid", None)

    if not width or not height or not grid:
        return []

    wanted = {room.pixel_value: room for room in rooms}
    sums: dict[int, list[int]] = {value: [0, 0, 0] for value in wanted}

    for index, value in enumerate(grid):
        acc = sums.get(value)
        if acc is None:
            continue
        acc[0] += index % width
        acc[1] += index // width
        acc[2] += 1

    result = []
    for value, room in wanted.items():
        sum_x, sum_y, count = sums[value]
        if not count:
            continue
        result.append(
            {
                "id": str(room.id),
                "name": room.name,
                "x": round(sum_x / count),
                "y": round(sum_y / count),
                "map_width": width,
                "map_height": height,
            }
        )

    return result
