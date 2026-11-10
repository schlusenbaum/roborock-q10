"""Helpers that work with the Q10 map API of python-roborock >= 7.12.

Since python-roborock 7.12 (Home Assistant 2026.10) the Q10
``MapContentTrait`` no longer exposes ``map_data``. The raw map is only
available as the latest ``Q10MapPacket`` (``_map_packet``), the rendered PNG
as ``image_content`` and the rooms as ``rooms``. Everything in this module
reads those attributes defensively so it keeps working if the library
changes again.
"""

from __future__ import annotations

import base64
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


# ---------------------------------------------------------------------------
# Last known map, kept across restarts
#
# After a restart a docked Q10 only sends its map during a cleaning run or
# when the Roborock app shows it. Until then the last received map and rooms
# are restored from storage, so rooms can be selected and cleaned right away.
# ---------------------------------------------------------------------------

_DOMAIN = "roborock_q10"
_CACHE_STORE_KEY = "roborock_q10.last_map"
_CACHE_STORE_VERSION = 1


async def async_load_map_cache(hass: Any) -> None:
    """Load the last known maps/rooms into hass.data."""
    from homeassistant.helpers.storage import Store

    store = Store(hass, _CACHE_STORE_VERSION, _CACHE_STORE_KEY)
    data = hass.data.setdefault(_DOMAIN, {})
    data["map_cache_store"] = store

    try:
        stored = await store.async_load() or {}
    except Exception as err:  # noqa: BLE001 - a broken cache must not block setup
        _LOGGER.warning("Q10 map cache could not be loaded: %s", err)
        stored = {}

    rooms = data.setdefault("rooms", {})
    maps = data.setdefault("maps", {})
    updated = data.setdefault("map_updated_at", {})

    for entity_id, item in stored.items():
        if item.get("rooms"):
            rooms.setdefault(entity_id, item["rooms"])
        if item.get("image"):
            try:
                maps.setdefault(entity_id, base64.b64decode(item["image"]))
            except ValueError:
                pass
        if item.get("updated_at"):
            updated.setdefault(entity_id, item["updated_at"])

    data["map_cache_loaded"] = set(stored)


def save_map_cache(hass: Any) -> None:
    """Schedule writing the current maps/rooms to storage."""
    data = hass.data.get(_DOMAIN, {})
    store = data.get("map_cache_store")

    if store is None:
        return

    def _data() -> dict[str, Any]:
        rooms = data.get("rooms", {})
        maps = data.get("maps", {})
        updated = data.get("map_updated_at", {})
        result = {}
        for entity_id in set(rooms) | set(maps):
            image = maps.get(entity_id)
            result[entity_id] = {
                "rooms": rooms.get(entity_id, []),
                "image": base64.b64encode(image).decode() if image else None,
                "updated_at": updated.get(entity_id),
            }
        return result

    store.async_delay_save(_data, 10)


def has_cached_map(hass: Any, vacuum_entity_id: str) -> bool:
    """Whether a map from a previous run is available."""
    return vacuum_entity_id in hass.data.get(_DOMAIN, {}).get(
        "map_cache_loaded", set()
    )


def room_list(hass: Any, vacuum_entity_id: str, api: Any = None) -> list[dict[str, Any]]:
    """Rooms as ``[{"id", "name"}]``: live from the robot, else last known."""
    live = get_rooms(api) if api is not None else []

    if live:
        return [{"id": int(room.id), "name": room.name} for room in live]

    return [
        {"id": int(room["id"]), "name": room["name"]}
        for room in hass.data.get(_DOMAIN, {})
        .get("rooms", {})
        .get(vacuum_entity_id, [])
    ]
