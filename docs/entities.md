# Entities

Die Integration ergänzt die ausgewählte Roborock-Vacuum-Entity um zusätzliche Home-Assistant-Entities.

## Sensoren

### Räume

Zeigt die Anzahl der aktuell erkannten Räume. Zusätzlich werden die Raumdaten als Attribute bereitgestellt.

Beispiel:

```yaml
rooms:
  - id: 1
    name: Corridor
  - id: 3
    name: Kitchen
  - id: 4
    name: Entrance Hall
```

### Kartenübersicht

Zeigt die Anzahl der bekannten Karten. Die Attribute enthalten unter anderem Karten-ID, Kartengröße, Anzahl der Räume und Raumnamen.

### Ausgewählte Räume

Zeigt die aktuell für die Reinigung ausgewählten Räume. Die Raumliste steht zusätzlich als Attribut zur Verfügung.

## Select-Entities

### Reinigungsraum

Die verfügbaren Optionen werden aus den aktuell bekannten Räumen der Q10-Karte erzeugt. `Alle` löscht die aktuelle Auswahl.

### Saugleistung

- Leise
- Normal
- Turbo
- Max
- Max+

### Wasserfluss

- Aus
- Niedrig
- Mittel
- Hoch

### Reinigungsroute

- Leicht
- Mittel
- Intensiv

## Button-Entities

### Karte aktualisieren

Fordert die aktuelle Karte erneut vom Roboter an.

### Ausgewählte Räume reinigen

Startet die Reinigung mit der aktuell ausgewählten Raumkonfiguration.

## Switch-Entity

### Automatische Kartenaktualisierung

Aktiviert beziehungsweise deaktiviert die periodische Kartenaktualisierung.

Bei aktiviertem Schalter wird alle 15 Minuten eine Kartenaktualisierung angefordert. Der Schaltzustand wird über Home Assistant wiederhergestellt.
