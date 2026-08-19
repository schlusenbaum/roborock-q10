import json
import logging

DOMAIN = "roborock_q10"

_LOGGER = logging.getLogger(__name__)


def diagnose_image(entity):
    from collections import Counter

    api = entity.coordinator.api
    image = api.map.image_content
    rooms = api.map.rooms or []

    if image is None:
        return {
            "image_type": None,
            "image_size": 0,
            "png_header": None,
            "rooms": [],
        }

    from PIL import Image
    import io

    pil_image = Image.open(io.BytesIO(image)).convert("RGB")
    colors = Counter(pil_image.getdata())

    return {
        "image_type": type(image).__name__,
        "image_size": len(image),
        "png_header": image[:8].hex(),
        "image_dimensions": pil_image.size,
        "rooms": [
            {
                "id": room.id,
                "name": room.name,
                "pixel_value": room.pixel_value,
                "pixel_color": (
                    room.pixel_value,
                    room.pixel_value,
                    room.pixel_value,
                ),
            }
            for room in rooms
        ],
        "top_colors": colors.most_common(20),
    }


def diagnose_map(entity):
    api = entity.coordinator.api
    map_api = api.map
    data = map_api.as_dict()

    return {
        "path": map_api.path,
        "rooms": [
            {
                "id": room.id,
                "name": room.name,
                "raw_name": room.raw_name,
                "pixel_value": room.pixel_value,
                "pixel_count": room.pixel_count,
            }
            for room in (map_api.rooms or [])
        ],
        "map_data_type": type(map_api.map_data).__name__,
        "as_dict_keys": list(data.keys()) if isinstance(data, dict) else None,
    }


def diagnose_objects(entity):
    result = {}

    objects = {
        "entity": entity,
        "coordinator": getattr(entity, "coordinator", None),
        "api": getattr(getattr(entity, "coordinator", None), "api", None),
    }

    api = objects["api"]

    if api is not None:
        objects["api_channel"] = getattr(api, "_channel", None)
        objects["api_channel_public"] = getattr(api, "channel", None)

    for name, obj in objects.items():
        result[name] = {
            "type": type(obj).__name__ if obj is not None else None,
            "module": type(obj).__module__ if obj is not None else None,
            "attributes": sorted(
                name for name in dir(obj)
                if not name.startswith("__")
            ) if obj is not None else [],
        }

    return result



async def diagnose_map_packets(entity, hass):
    from roborock.map.b01_q10_map_parser import Q10MapPacket
    from roborock.devices.rpc.b01_q10_channel import decode_message

    api = entity.coordinator.api
    channel = api._channel

    listeners = hass.data.setdefault("roborock_q10", {}).setdefault(
        "diagnostic_listeners", {}
    )

    entity_id = entity.entity_id

    if entity_id in listeners:
        return {
            "status": "already_registered",
            "entity_id": entity_id,
        }

    def callback(message):
        try:
            decoded = decode_message(message)
        except Exception as ex:
            _LOGGER.warning(
                "Q10 DECODE ERROR: type=%s error=%s",
                type(message).__name__,
                ex,
            )
            return

        if isinstance(decoded, Q10MapPacket):
            packet_cache = hass.data.setdefault("roborock_q10", {}).setdefault(
                "packet_cache", {}
            )

            packet_cache[entity_id] = {
                "map_id": decoded.map_id,
                "width": decoded.width,
                "height": decoded.height,
                "grid": bytes(decoded.grid),
                "rooms": [
                    {
                        "id": room.id,
                        "name": room.name,
                        "raw_name": room.raw_name,
                        "pixel_value": room.pixel_value,
                    }
                    for room in decoded.rooms
                ],
            }

            _LOGGER.warning(
                "Q10 GRID CACHE: entity=%s map_id=%s size=%sx%s grid_bytes=%s",
                entity_id,
                decoded.map_id,
                decoded.width,
                decoded.height,
                len(decoded.grid),
            )

    unsubscribe = await channel.subscribe(callback)
    listeners[entity_id] = unsubscribe

    return {
        "status": "registered",
        "entity_id": entity_id,
        "channel_type": type(channel).__name__,
        "packet_type": Q10MapPacket.__name__,
    }



def register_map_cache(entity, hass):
    api = entity.coordinator.api

    cache = hass.data.setdefault("roborock_q10", {}).setdefault(
        "map_cache", {}
    )

    patched = hass.data.setdefault("roborock_q10", {}).setdefault(
        "map_cache_patches", {}
    )

    entity_id = entity.entity_id

    if entity_id in patched:
        return {
            "status": "already_registered",
            "entity_id": entity_id,
            "maps": list(cache.get(entity_id, {}).keys()),
        }

    original_handle_message = api._handle_message

    def wrapped_handle_message(message):
        from roborock.map.b01_q10_map_parser import Q10MapPacket

        if isinstance(message, Q10MapPacket):
            maps = cache.setdefault(entity_id, {})

            original_handle_message(message)

            image_content = api.map.image_content
            map_data = api.map.map_data

            maps[str(message.map_id)] = {
                "map_id": message.map_id,
                "width": message.width,
                "height": message.height,
                "rooms": [
                    {
                        "id": room.id,
                        "raw_name": room.raw_name,
                        "pixel_value": room.pixel_value,
                    }
                    for room in message.rooms
                ],
                "image_content_type": (
                    type(image_content).__name__
                    if image_content is not None
                    else None
                ),
                "image_content_size": (
                    len(image_content)
                    if image_content is not None
                    else 0
                ),
                "image_content_header": (
                    image_content[:8].hex()
                    if image_content is not None
                    else None
                ),
                "map_data_type": (
                    type(map_data).__name__
                    if map_data is not None
                    else None
                ),
            }

            _LOGGER.warning(
                "Q10 MAP CACHE: entity=%s map_id=%s maps=%s image=%s bytes=%s",
                entity_id,
                message.map_id,
                list(maps.keys()),
                type(image_content).__name__ if image_content is not None else None,
                len(image_content) if image_content is not None else 0,
            )

            return

        return original_handle_message(message)

    api._handle_message = wrapped_handle_message
    patched[entity_id] = original_handle_message

    return {
        "status": "registered",
        "entity_id": entity_id,
        "maps": list(cache.get(entity_id, {}).keys()),
    }


def diagnose_handle_message(entity, hass):
    api = entity.coordinator.api

    listeners = hass.data.setdefault("roborock_q10", {}).setdefault(
        "diagnostic_handle_listeners", {}
    )

    entity_id = entity.entity_id

    if entity_id in listeners:
        return {
            "status": "already_registered",
            "entity_id": entity_id,
        }

    original_handle_message = api._handle_message

    def wrapped_handle_message(message):
        from roborock.map.b01_q10_map_parser import Q10MapPacket

        if isinstance(message, Q10MapPacket):
            from collections import Counter

            counts = Counter(message.grid)

            room_info = [
                {
                    "id": room.id,
                    "name": room.name,
                    "raw_name": room.raw_name,
                    "pixel_value": room.pixel_value,
                    "grid_count": counts.get(room.pixel_value, 0),
                }
                for room in message.rooms
            ]

            _LOGGER.warning(
                "Q10 GRID: map_id=%s size=%sx%s grid_bytes=%s rooms=%s",
                message.map_id,
                message.width,
                message.height,
                len(message.grid),
                room_info,
            )

        return original_handle_message(message)

    api._handle_message = wrapped_handle_message
    listeners[entity_id] = original_handle_message

    return {
        "status": "registered",
        "entity_id": entity_id,
        "patched_method": "_handle_message",
    }


def diagnose_map_listener(entity, hass):
    api = entity.coordinator.api
    map_api = api.map

    listeners = hass.data.setdefault("roborock_q10", {}).setdefault(
        "diagnostic_map_listeners", {}
    )

    entity_id = entity.entity_id

    if entity_id in listeners:
        return {
            "status": "already_registered",
            "entity_id": entity_id,
        }

    def map_updated():
        map_data = map_api.map_data

        result = {
            "path": map_api.path,
            "rooms": [
                {
                    "id": room.id,
                    "name": room.name,
                    "raw_name": room.raw_name,
                    "pixel_value": room.pixel_value,
                    "pixel_count": room.pixel_count,
                }
                for room in (map_api.rooms or [])
            ],
            "map_data_type": type(map_data).__name__ if map_data is not None else None,
            "map_name": getattr(map_data, "map_name", None),
            "vacuum_room": getattr(map_data, "vacuum_room", None),
            "vacuum_room_name": getattr(map_data, "vacuum_room_name", None),
            "map_data_attributes": sorted(
                name for name in dir(map_data)
                if not name.startswith("__")
            ) if map_data is not None else [],
        }

        _LOGGER.warning(
            "Q10 MAP LISTENER: %s",
            result,
        )

    unsubscribe = map_api.add_update_listener(map_updated)
    listeners[entity_id] = unsubscribe

    return {
        "status": "registered",
        "entity_id": entity_id,
        "listener_type": "MapContentTrait.add_update_listener",
    }


async def diagnose(entity, mode="map", hass=None):
    if mode == "map":
        return diagnose_map(entity)
    if mode == "objects":
        return diagnose_objects(entity)
    if mode == "map_packets":
        if hass is None:
            raise ValueError("Home Assistant instance required")
        return await diagnose_map_packets(entity, hass)
    if mode == "map_listener":
        if hass is None:
            raise ValueError("Home Assistant instance required")
        return diagnose_map_listener(entity, hass)
    if mode == "handle_message":
        if hass is None:
            raise ValueError("Home Assistant instance required")
        return diagnose_handle_message(entity, hass)
    if mode == "map_cache":
        if hass is None:
            raise ValueError("Home Assistant instance required")
        return register_map_cache(entity, hass)
    if mode == "map_store":
        if hass is None:
            raise ValueError("Home Assistant instance required")

        maps = hass.data.get(DOMAIN, {}).get("maps", {})
        image_content = maps.get(entity.entity_id)

        return {
            "status": "ok" if image_content is not None else "no_image",
            "entity_id": entity.entity_id,
            "image_type": (
                type(image_content).__name__
                if image_content is not None
                else None
            ),
            "image_size": (
                len(image_content)
                if image_content is not None
                else 0
            ),
            "png_header": (
                image_content[:8].hex()
                if image_content is not None
                else None
            ),
        }
    if mode == "image":
        return diagnose_image(entity)

    raise ValueError(f"Unknown diagnostic mode: {mode}")
