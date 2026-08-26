# Services

The integration provides services under the `roborock_q10` domain.

## Get Rooms

Service:

`roborock_q10.get_rooms`

Required data:

```yaml
entity_id: vacuum.your_q10
```

The service registers the required map listener and refreshes the Roborock API if room information is not yet available.

## Select Rooms

Service:

`roborock_q10.select_rooms`

Example:

```yaml
entity_id: vacuum.your_q10
room_names:
  - Kitchen
  - Living Room
```

The selected room names are validated against the rooms known by the integration.

## Clean Rooms

Service:

`roborock_q10.clean_rooms`

Rooms can be specified by ID:

```yaml
entity_id: vacuum.your_q10
room_ids:
  - 16
  - 17
```

Or by name:

```yaml
entity_id: vacuum.your_q10
room_names:
  - Kitchen
  - Living Room
```

If no room IDs or names are supplied, the integration uses the previously selected rooms.

## Diagnostics

Service:

`roborock_q10.diagnose`

Example:

```yaml
entity_id: vacuum.your_q10
mode: map
```

Diagnostic modes are intended primarily for development and troubleshooting.
