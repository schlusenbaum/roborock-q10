import asyncio
import logging

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.vacuum import DATA_COMPONENT
from homeassistant.core import HomeAssistant, EVENT_STATE_CHANGED
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import discovery
from .diagnostics import diagnose
from .map_helpers import get_map_packet, request_map, room_centroids

_LOGGER = logging.getLogger(__name__)


DOMAIN = "roborock_q10"
WS_GET_ROOMS = "roborock_q10/get_rooms"
EVENT_MAP_UPDATED = "roborock_q10_map_updated"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS = ["switch", "sensor", "select", "button", "image"]


def _register_q10_packet_listener(hass, entity):
    """Store decoded Q10 map packets without modifying the Roborock core."""
    listeners = hass.data.setdefault(DOMAIN, {}).setdefault(
        "packet_listeners", {}
    )

    entity_id = entity.entity_id

    if entity_id in listeners:
        return

    api = entity.coordinator.api
    original_handle_message = api._handle_message

    def wrapped_handle_message(message):
        from roborock.map.b01_q10_map_parser import Q10MapPacket

        if isinstance(message, Q10MapPacket):
            _LOGGER.debug(
                "Q10 PACKET RECEIVED map_id=%s rooms=%s",
                message.map_id,
                len(message.rooms),
            )
            maps = hass.data.setdefault(DOMAIN, {}).setdefault(
                "packets", {}
            ).setdefault(entity_id, {})

            maps[str(message.map_id)] = {
                "map_id": message.map_id,
                "width": message.width,
                "height": message.height,
                "grid": bytes(message.grid),
                "rooms": [
                    {
                        "id": room.id,
                        "name": room.name,
                        "raw_name": room.raw_name,
                        "pixel_value": room.pixel_value,
                    }
                    for room in message.rooms
                ],
            }

            _LOGGER.debug(
                "Q10 MAP EVENT FIRE: %s",
                entity_id,
            )

            hass.bus.async_fire(
                EVENT_MAP_UPDATED,
                {"entity_id": entity_id},
            )

        return original_handle_message(message)

    api._handle_message = wrapped_handle_message
    listeners[entity_id] = original_handle_message


def _room_data(entity):
    """Room label positions, computed from the raw Q10 map grid."""
    return room_centroids(entity.coordinator.api)


def _register_map_listener(hass, entity):
    """Register one throttled listener for this Q10 map."""
    listeners = hass.data.setdefault(DOMAIN, {}).setdefault("listeners", {})

    entity_id = entity.entity_id
    api = entity.coordinator.api

    existing = listeners.get(entity_id)
    if existing is not None:
        old_api, old_unsub = existing
        if old_api is api:
            return
        # The core Roborock integration was reloaded and created a new API
        # object: drop the stale listener and subscribe to the new one.
        try:
            old_unsub()
        except Exception:  # noqa: BLE001
            pass

    last_fire = 0.0

    def map_updated(force=False):
        nonlocal last_fire

        _LOGGER.debug("Q10 MAP UPDATE CALLBACK ausgelöst")

        now = hass.loop.time()

        if now - last_fire < 1.0 and not force:
            return

        last_fire = now

        image_content = entity.coordinator.api.map.image_content
        _LOGGER.debug(
            "Q10 MAP IMAGE CONTENT: %s bytes",
            len(image_content) if image_content is not None else None,
        )

        if image_content is not None:
            hass.data.setdefault(DOMAIN, {}).setdefault("maps", {})[
                entity_id
            ] = image_content

            hass.bus.async_fire(
                EVENT_MAP_UPDATED,
                {"entity_id": entity_id},
            )

        map_packet = getattr(entity.coordinator.api.map, "_map_packet", None)
        map_id = getattr(map_packet, "map_id", None)
        rooms = entity.coordinator.api.map.rooms or []
        _LOGGER.debug(
            "Q10 MAP UPDATE ROOMS: %s",
            [(room.id, room.name) for room in rooms],
        )

        hass.data.setdefault(DOMAIN, {}).setdefault("rooms", {})[
            entity_id
        ] = [
            {
                "id": room.id,
                "name": room.name,
                "map_id": map_id,
                "pixel_value": room.pixel_value,
                "pixel_count": room.pixel_count,
            }
            for room in rooms
        ]

    listeners[entity_id] = (api, api.map.add_update_listener(map_updated))

    # A map that arrived before we subscribed would otherwise never show up.
    map_updated(force=True)
    _LOGGER.debug(
        "Q10 MAP LISTENER REGISTRIERT: %s",
        entity_id,
    )

async def handle_get_rooms(call):
    import logging


    entity_id = call.data["entity_id"]
    entity = call.hass.data[DATA_COMPONENT].get_entity(entity_id)

    if entity is None:
        raise ValueError(f"Entity not found: {entity_id}")



    _LOGGER.debug(
        "Q10 GET_ROOMS: entity=%s gefunden",
        entity_id,
    )

    _register_map_listener(call.hass, entity)

    rooms = entity.coordinator.api.map.rooms or []

    if not rooms:
        await request_map(entity.coordinator.api)
        for _ in range(25):
            rooms = entity.coordinator.api.map.rooms or []
            if rooms:
                break
            await asyncio.sleep(0.2)

    rooms = [
        {
            "id": room.id,
            "name": room.name,
        }
        for room in rooms
    ]

    call.hass.data.setdefault(DOMAIN, {}).setdefault("rooms", {})[entity_id] = rooms

    _LOGGER.debug(
        "Q10 GET_ROOMS: liefert %s Räume: %s",
        len(rooms),
        rooms,
    )

WS_DIAGNOSTICS = "roborock_q10/diagnostics"


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_DIAGNOSTICS,
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("mode", default="map"): str,
    }
)
@websocket_api.async_response
async def websocket_diagnostics(hass, connection, msg):
    component = hass.data[DATA_COMPONENT]
    entity = component.get_entity(msg["entity_id"])

    if entity is None:
        connection.send_error(
            msg["id"],
            "entity_not_found",
            "Vacuum entity not found",
        )
        return

    if msg["mode"] != "map":
        connection.send_error(
            msg["id"],
            "unknown_mode",
            f"Unknown diagnostic mode: {msg['mode']}",
        )
        return

    connection.send_result(
        msg["id"],
        diagnose_map(entity),
    )

@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_GET_ROOMS,
        vol.Required("entity_id"): cv.entity_id,
    }
)
@websocket_api.async_response
async def websocket_get_rooms(hass, connection, msg):
    component = hass.data[DATA_COMPONENT]
    entity = component.get_entity(msg["entity_id"])

    if entity is not None:
        _register_q10_packet_listener(hass, entity)

    if entity is None:
        connection.send_error(
            msg["id"],
            "entity_not_found",
            "Vacuum entity not found",
        )
        return

    _register_map_listener(hass, entity)

    rooms = _room_data(entity)

    if not rooms:
        await request_map(entity.coordinator.api)

        for _ in range(25):
            rooms = _room_data(entity)

            if rooms:
                break

            await asyncio.sleep(0.2)

    connection.send_result(
        msg["id"],
        {
            "entity_id": msg["entity_id"],
            "rooms": rooms,
        },
    )


async def handle_clean_rooms(hass, call):
    """Start cleaning selected Q10 rooms."""
    import logging


    entity_id = call.data["entity_id"]

    room_ids = [
        int(room_id)
        for room_id in call.data.get("room_ids", [])
    ]

    entity = hass.data[DATA_COMPONENT].get_entity(entity_id)

    if entity is None:
        raise ValueError(f"Entity not found: {entity_id}")

    room_names = call.data.get("room_names", [])

    if not room_ids and not room_names:
        selected_rooms = (
            hass.data.get(DOMAIN, {})
            .get("selected_rooms", {})
            .get(entity_id, [])
        )

        if selected_rooms:
            if isinstance(selected_rooms, str):
                room_names = [selected_rooms]
            else:
                room_names = list(selected_rooms)
        else:
            rooms = entity.coordinator.api.map.rooms or []

            if not rooms:
                raise ValueError(
                    "Q10 rooms are not available yet. Please try again."
                )

            room_ids = [room.id for room in rooms]

    if room_names:
        rooms = entity.coordinator.api.map.rooms or []

        name_to_id = {
            room.name: room.id
            for room in rooms
        }

        for name in room_names:
            if name not in name_to_id:
                raise ValueError(
                    f"Unknown Q10 room name: {name}. Available: {list(name_to_id)}"
                )

            room_ids.append(name_to_id[name])

    known_rooms = (
        hass.data.get(DOMAIN, {})
        .get("rooms", {})
        .get(entity_id, [])
    )

    if known_rooms:
        known_ids = {int(room["id"]) for room in known_rooms}
        unknown_ids = [
            room_id for room_id in room_ids
            if room_id not in known_ids
        ]

        if unknown_ids:
            raise ValueError(
                f"Unknown Q10 room id(s): {unknown_ids}. Available: {sorted(known_ids)}"
            )

    await entity.coordinator.api.vacuum.clean_segments(room_ids)


async def handle_select_rooms(hass, call):
    """Store selected Q10 rooms for later cleaning."""
    entity_id = call.data["entity_id"]
    room_names = call.data.get("room_names", [])

    if isinstance(room_names, str):
        room_names = [room_names]
    else:
        room_names = list(room_names)

    entity = hass.data[DATA_COMPONENT].get_entity(entity_id)

    if entity is None:
        raise ValueError(f"Entity not found: {entity_id}")

    rooms = entity.coordinator.api.map.rooms or []

    available = {room.name for room in rooms}

    unknown = [
        name for name in room_names
        if name not in available
    ]

    if unknown:
        raise ValueError(
            f"Unknown Q10 room name(s): {unknown}. Available: {sorted(available)}"
        )

    hass.data.setdefault(DOMAIN, {}).setdefault(
        "selected_rooms", {}
    )[entity_id] = room_names

    hass.bus.async_fire(
        "roborock_q10_selected_rooms_updated",
        {
            "entity_id": entity_id,
        },
    )

async def async_setup(hass: HomeAssistant, config) -> bool:
    """Set up the Roborock Q10 helper."""
    component = hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN]["listeners"] = {}

    async def handle_diagnose(call):
        entity_id = call.data["entity_id"]
        mode = call.data.get("mode", "map")
        entity = hass.data[DATA_COMPONENT].get_entity(entity_id)

        if entity is None:
            raise ValueError(f"Entity not found: {entity_id}")

        result = await diagnose(entity, mode, hass)

        _LOGGER.debug("Q10 DIAGNOSTICS [%s]: %s", mode, result)

    hass.services.async_register(
        DOMAIN,
        "diagnose",
        handle_diagnose,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("mode", default="map"): str,
        }),
    )

    hass.services.async_register(
        DOMAIN,
        "get_rooms",
        handle_get_rooms,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
        }),
    )

    async def select_rooms_service(call):
        await handle_select_rooms(hass, call)

    hass.services.async_register(
        DOMAIN,
        "select_rooms",
        select_rooms_service,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Required("room_names"): [str],
        }),
    )

    async def clean_rooms_service(call):
        await handle_clean_rooms(hass, call)

    hass.services.async_register(
        DOMAIN,
        "clean_rooms",
        clean_rooms_service,
        schema=vol.Schema({
            vol.Required("entity_id"): cv.entity_id,
            vol.Optional("room_ids", default=[]): [int],
            vol.Optional("room_names", default=[]): [str],
        }),
    )

    websocket_api.async_register_command(hass, websocket_get_rooms)
    websocket_api.async_register_command(hass, websocket_diagnostics)

    return True


async def _async_initial_map_request(entity, attempts=3, wait=10.0):
    """Request the map after startup until a map packet has arrived.

    After a Home Assistant restart the Q10 does not always push its full map
    on its own (it often only does so once the Roborock app opens the map).
    Ask a few times, bounded, and stop as soon as a packet is there.
    """
    api = entity.coordinator.api

    for attempt in range(1, attempts + 1):
        if get_map_packet(api) is not None:
            return

        _LOGGER.debug("Q10 initial map request, attempt %s/%s", attempt, attempts)
        await request_map(api)

        for _ in range(int(wait / 0.5)):
            if get_map_packet(api) is not None:
                return
            await asyncio.sleep(0.5)

    _LOGGER.warning(
        "Q10 map was not received after %s requests. Open the map once in "
        "the Roborock app or press the map refresh button",
        attempts,
    )


async def async_setup_entry(hass, entry):
    _LOGGER.debug(
        "Q10 SETUP_ENTRY ERREICHT: %s",
        entry.entry_id,
    )

    entity_id = entry.data.get("entity_id")

    if not entity_id:
        return True

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    for _ in range(25):
        entity = hass.data[DATA_COMPONENT].get_entity(entity_id)

        if entity is not None:
            _register_map_listener(hass, entity)
            entry.async_create_background_task(
                hass,
                _async_initial_map_request(entity),
                f"{DOMAIN}_initial_map_request_{entity_id}",
            )
            break

        await asyncio.sleep(0.2)

    return True



async def async_unload_entry(hass, entry):
    entity_id = entry.data.get("entity_id")

    if not entity_id:
        return True

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    listener = hass.data.get(DOMAIN, {}).get("listeners", {}).pop(entity_id, None)
    if listener is not None:
        try:
            listener[1]()
        except Exception:  # noqa: BLE001
            pass

    return unloaded
