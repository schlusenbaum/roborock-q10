"""Helpers that work with the Q10 map API of python-roborock >= 7.12.

Since python-roborock 7.12 (Home Assistant 2026.10) the Q10
``MapContentTrait`` no longer exposes ``map_data``. The raw map is only
available as the latest ``Q10MapPacket`` (``_map_packet``), the rendered PNG
as ``image_content`` and the rooms as ``rooms``. Everything in this module
reads those attributes defensively so it keeps working if the library
changes again.
"""

from __future__ import annotations

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


async def request_map(api: Any) -> None:
    """Ask the robot to push its current map.

    1. ``api.map.refresh()`` - read-only current-map request of the library.
    2. Live-map heartbeat ``COMMON {"110": 1}`` - what the Roborock app sends
       while its map screen is open. Some firmware only pushes the full map
       after this. Failures are logged and ignored.
    """
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
