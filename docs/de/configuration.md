# Konfiguration

Die Integration verwendet die bestehende Roborock-Vacuum-Entity als Bezugspunkt.

## Grundprinzip

Die offizielle Roborock-Integration stellt unter anderem Vacuum-Entity, Coordinator, Roborock-API sowie Karten- und Statusdaten bereit.

Die Q10-Integration verwendet diese Daten und ergänzt Q10-spezifische Funktionen.

## Gerätezuordnung

Die zusätzlichen Entities werden nach ihrer Erstellung dem Gerät der ausgewählten Vacuum-Entity zugeordnet.

Dadurch erscheinen die zusätzlichen Q10-Entities beim gleichen Home-Assistant-Gerät wie der Roboter.

## Keine zweite Verbindung

Die Q10-Integration baut keine separate Roborock-Anmeldung und keine zweite Geräteverbindung auf.

Änderungen oder Inkompatibilitäten in der offiziellen Roborock-Integration beziehungsweise der darunterliegenden `roborock`-Bibliothek können daher Auswirkungen auf diese Integration haben.
