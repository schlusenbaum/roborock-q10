# Roborock Q10

Home-Assistant-Custom-Integration für Roborock-Q10-Geräte.

Die Integration erweitert die offizielle Home-Assistant-Roborock-Integration um Q10-spezifische Funktionen für Karten, Räume und Reinigung.

> **Wichtig:** Die Integration ersetzt die offizielle Roborock-Integration nicht. Sie verwendet die bereits vorhandene Roborock-Vacuum-Entity und ergänzt sie um zusätzliche Entities und Dienste.

## Funktionen

- Räume direkt aus der Q10-Karte auslesen
- Raum-IDs und Raumnamen bereitstellen
- bekannte Q10-Karten katalogisieren
- Karte manuell aktualisieren
- Kartenaktualisierung automatisch alle 15 Minuten ausführen
- Reinigungsraum auswählen
- ausgewählte Räume reinigen
- Räume per ID oder Name über Services reinigen
- Saugleistung einstellen
- Wasserfluss einstellen
- Reinigungsroute einstellen
- Diagnose- und WebSocket-Funktionen bereitstellen

## Voraussetzungen

- Home Assistant
- die offizielle Home-Assistant-Roborock-Integration
- ein über die offizielle Home-Assistant-Roborock-Integration eingerichteter Roborock Q10

## Dokumentation

- [Installation](docs/installation.md)
- [Konfiguration](docs/configuration.md)
- [Entities](docs/entities.md)
- [Räume und Karten](docs/rooms-and-maps.md)
- [Services](docs/services.md)
- [Automationen](docs/automations.md)
- [Fehlerbehebung](docs/troubleshooting.md)
- [Entwicklung](docs/development.md)

## Technischer Überblick

Die Q10-Integration greift auf die bestehende Vacuum-Entity, deren Coordinator und API der offiziellen Roborock-Integration zu. Sie baut keine zweite Roborock-Verbindung und kein zweites physisches Gerät auf.

```text
Roborock Q10
    |
    v
offizielle Roborock-Integration
    |
    v
Vacuum-Entity / Coordinator / API
    |
    v
Roborock Q10 Custom Integration
    +-- Karten
    +-- Räume
    +-- Reinigung
    +-- Q10-Einstellungen
    +-- Diagnose
```

## Lizenz

MIT
