# Räume und Karten

Die Q10-Integration liest die Raumdaten aus den vom Roboter gelieferten Kartendaten.

## Raumdaten

Für erkannte Räume stehen unter anderem Raum-ID, Raumname und der für die Kartenauswertung benötigte Pixelwert zur Verfügung.

Die Raumdaten werden für die Home-Assistant-Entities und für die Raumreinigung verwendet.

## Kartenkatalog

Die Integration führt pro Vacuum-Entity einen Katalog der empfangenen Karten.

Für jede bekannte Karte werden unter anderem gespeichert:

- Karten-ID
- Breite
- Höhe
- Raumliste
- Raum-ID
- Raumname

Die Entity **Kartenübersicht** stellt diese Informationen in Home Assistant dar.

## Kartenaktualisierung

Eine Karte kann über den Button **Karte aktualisieren** erneut angefordert werden.

Alternativ kann die automatische Kartenaktualisierung aktiviert werden. In diesem Fall wird alle 15 Minuten eine Aktualisierung angefordert.

## Räume aktualisieren

Der Service `roborock_q10.get_rooms` stellt sicher, dass Raumdaten vorhanden sind. Falls noch keine Räume verfügbar sind, wird eine Aktualisierung der Karte angefordert und anschließend auf die Raumdaten gewartet.

## Raumreinigung

Für die Reinigung können Räume anhand ihres Namens oder ihrer ID angegeben werden.

Bei der Verwendung von Raumnamen werden diese anhand der aktuell bekannten Q10-Raumdaten in die zugehörigen Raum-IDs übersetzt.

Unbekannte Räume werden abgewiesen.
