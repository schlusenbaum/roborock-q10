# Automations

The Q10 integration can be used in Home Assistant automations through its entities and services.

## Clean Selected Rooms

Example:

```yaml
alias: Clean kitchen and living room
sequence:
  - service: roborock_q10.select_rooms
    target:
      entity_id: vacuum.your_q10
    data:
      room_names:
        - Kitchen
        - Living Room

  - service: roborock_q10.clean_rooms
    target:
      entity_id: vacuum.your_q10
```

## Clean Rooms Directly

Room names can also be supplied directly:

```yaml
alias: Clean kitchen
sequence:
  - service: roborock_q10.clean_rooms
    target:
      entity_id: vacuum.your_q10
    data:
      room_names:
        - Kitchen
```

## Use Room IDs

If stable room IDs are known, they can be used directly:

```yaml
service: roborock_q10.clean_rooms
target:
  entity_id: vacuum.your_q10
data:
  room_ids:
    - 16
```
