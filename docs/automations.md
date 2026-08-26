# Automationen

Die zusätzlichen Services und Entities können in Home-Assistant-Automationen verwendet werden.

## Räume regelmäßig reinigen

```yaml
alias: Q10 Küche und Wohnzimmer reinigen
trigger:
  - platform: time
    at: "10:00:00"

action:
  - service: roborock_q10.clean_rooms
    data:
      entity_id: vacuum.roborock_q10
      room_names:
        - Küche
        - Wohnzimmer
```

## Raum auswählen und anschließend reinigen

```yaml
action:
  - service: roborock_q10.select_rooms
    data:
      entity_id: vacuum.roborock_q10
      room_names:
        - Küche
        - Flur

  - service: roborock_q10.clean_rooms
    data:
      entity_id: vacuum.roborock_q10
```

Entity-IDs können abhängig von der jeweiligen Home-Assistant-Konfiguration anders lauten.
