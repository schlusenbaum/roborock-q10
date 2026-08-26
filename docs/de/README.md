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

### Deutsch

- **[Installation](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/installation.md)**
- **[Konfiguration](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/configuration.md)**
- **[Entities](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/entities.md)**
- **[Räume und Karten](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/rooms-and-maps.md)**
- **[Services](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/services.md)**
- **[Automationen](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/automations.md)**
- **[Fehlerbehebung](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/troubleshooting.md)**
- **[Entwicklung](https://github.com/schlusenbaum/roborock-q10/blob/main/docs/de/development.md)**

### English

**[English documentation](https://github.com/schlusenbaum/roborock-q10/blob/main/README.md)**

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
