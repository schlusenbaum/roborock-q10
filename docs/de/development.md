# Entwicklung

## Repository-Struktur

```text
roborock-q10/
├── README.md
├── hacs.json
├── docs/
│   ├── installation.md
│   ├── configuration.md
│   ├── entities.md
│   ├── rooms-and-maps.md
│   ├── services.md
│   ├── automations.md
│   ├── troubleshooting.md
│   └── development.md
└── custom_components/
    └── roborock_q10/
        ├── __init__.py
        ├── button.py
        ├── config_flow.py
        ├── diagnostics.py
        ├── manifest.json
        ├── select.py
        ├── sensor.py
        ├── services.yaml
        └── switch.py
```

## Module

| Datei | Aufgabe |
|---|---|
| `__init__.py` | Setup, Kartenverarbeitung, Services und WebSocket-API |
| `config_flow.py` | Home-Assistant-Konfigurationsdialog |
| `sensor.py` | Räume, Kartenübersicht und ausgewählte Räume |
| `select.py` | Wasserfluss, Reinigungsraum, Saugleistung und Reinigungsroute |
| `button.py` | Kartenaktualisierung und Reinigung ausgewählter Räume |
| `switch.py` | automatische Kartenaktualisierung |
| `diagnostics.py` | Diagnoseinformationen |
| `services.yaml` | Beschreibung der Home-Assistant-Services |
| `manifest.json` | Integrationsmetadaten |

## Architektur

Die Integration nutzt die bereits vorhandene Roborock-Vacuum-Entity und deren Coordinator/API.

```text
Vacuum Entity
    |
    +-- coordinator
    |      |
    |      +-- API
    |
    +-- map
    |      +-- rooms
    |      +-- map data
    |
    +-- status
           +-- fan level
           +-- water level
           +-- cleaning route
```

## Kartenverarbeitung

Beim Empfang von Kartendaten werden Raum- und Karteninformationen extrahiert und intern katalogisiert. Anschließend werden Home-Assistant-Events ausgelöst, sodass die zugehörigen Entities ihren Zustand aktualisieren können.

## Raumreinigung

Die Raumreinigung kann mit Raum-IDs oder Raumnamen aufgerufen werden.

```text
Raumname
   |
   v
bekannte Q10-Räume
   |
   v
Raum-ID
   |
   v
Reinigungsbefehl
```

Unbekannte Räume werden vor dem Senden des Befehls abgewiesen.

## Gerätezuordnung

Die zusätzlichen Entities werden nach ihrer Erstellung der `device_id` der bestehenden Vacuum-Entity zugeordnet. Dadurch gehören sie zum gleichen Home-Assistant-Gerät wie der Roboter.

## Abhängigkeiten

Die Q10-Integration verwendet Datenstrukturen und APIs der offiziellen Roborock-Integration beziehungsweise der installierten `roborock`-Python-Bibliothek.

Änderungen an diesen Schnittstellen können Anpassungen der Q10-Integration erforderlich machen.

## Entwicklungshinweise

Vor Änderungen:

```bash
git status
git log -1 --oneline
```

Nach Änderungen:

```bash
git diff
git status
```

Vor einem Commit sollte die Integration in Home Assistant getestet werden.

## Lizenz

MIT
