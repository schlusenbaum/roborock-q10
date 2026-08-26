# Services

## `roborock_q10.get_rooms`

Ruft die aktuellen Räume des Roboters ab.

```yaml
service: roborock_q10.get_rooms
data:
  entity_id: vacuum.roborock_q10
```

Wenn noch keine Raumdaten vorhanden sind, fordert die Integration zunächst eine aktuelle Karte an.

## `roborock_q10.select_rooms`

Speichert eine Auswahl von Räumen anhand ihrer Namen.

```yaml
service: roborock_q10.select_rooms
data:
  entity_id: vacuum.roborock_q10
  room_names:
    - Küche
    - Wohnzimmer
```

## `roborock_q10.clean_rooms`

Startet die Reinigung bestimmter Räume.

### Über Raum-IDs

```yaml
service: roborock_q10.clean_rooms
data:
  entity_id: vacuum.roborock_q10
  room_ids:
    - 3
    - 6
```

### Über Raumnamen

```yaml
service: roborock_q10.clean_rooms
data:
  entity_id: vacuum.roborock_q10
  room_names:
    - Küche
    - Wohnzimmer
```

Wenn weder `room_ids` noch `room_names` angegeben werden, verwendet der Service die aktuell gespeicherte Raumwahl.

Die Integration prüft die angegebenen Räume gegen die bekannten Q10-Raumdaten.

## `roborock_q10.diagnose`

Führt eine Diagnose aus.

```yaml
service: roborock_q10.diagnose
data:
  entity_id: vacuum.roborock_q10
  mode: map
```

Der aktuell vorgesehene Diagnosemodus ist `map`.

## WebSocket

Zusätzlich stellt die Integration Q10-spezifische WebSocket-Kommandos bereit, insbesondere zum Abrufen der Raumdaten und von Diagnoseinformationen. Diese Schnittstelle ist vor allem für Custom Cards und andere Frontends interessant.
