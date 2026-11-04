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

Fordert die aktuelle Karte beim Roboter an.

> **Hinweis:** Seit Home Assistant 2026.10 (python-roborock 7.12) schickt der Q10 im Dock auf diese Anfrage meist **keine** Karte, sondern nur Statuswerte. Die Karte kommt zuverlässig während einer Reinigung oder wenn die Kartenansicht in der Roborock-App geöffnet wird.

### Ausgewählte Räume reinigen

Startet die Reinigung mit der aktuell ausgewählten Raumkonfiguration.

## Switch-Entity

### Automatische Kartenaktualisierung

Fordert bei aktiviertem Schalter alle 15 Minuten eine Kartenaktualisierung an. Der Schaltzustand wird über Home Assistant wiederhergestellt.

Bei neuen Installationen ist die Entity standardmäßig deaktiviert, weil der Roboter im Dock auf die Anfrage meist nicht reagiert (siehe **Karte aktualisieren**).
