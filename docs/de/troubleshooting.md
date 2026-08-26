# Fehlerbehebung

## Keine Räume werden angezeigt

Prüfen, ob die offizielle Roborock-Vacuum-Entity verfügbar ist.

Danach `roborock_q10.get_rooms` mit der richtigen `entity_id` ausführen. Wenn noch keine Raumdaten vorliegen, fordert die Integration eine aktuelle Karte an.

## Räume werden nicht aktualisiert

Eine manuelle Kartenaktualisierung über **Karte aktualisieren** ausführen.

Falls das Problem regelmäßig auftritt, kann die **Automatische Kartenaktualisierung** aktiviert werden.

## Q10-Integration findet die Vacuum-Entity nicht

Prüfen, ob die in der Q10-Konfiguration angegebene Entity tatsächlich existiert, zum Beispiel `vacuum.roborock_q10`.

## Zusätzliche Entities erscheinen bei einem falschen Gerät

Die Q10-Entities werden nach ihrer Erstellung dem Gerät der konfigurierten Vacuum-Entity zugeordnet. Nach Änderungen an der Geräte- oder Entity-Konfiguration sollte die Entity Registry geprüft werden.

## Reinigung eines Raumes schlägt fehl

Prüfen:

1. Ist die Karte aktuell?
2. Ist der Raumname exakt so vorhanden, wie er von der Q10-Karte geliefert wird?
3. Existiert die verwendete Raum-ID?
4. Ist der Roboter erreichbar?

Bei `room_names` übersetzt die Integration die Namen anhand der aktuell bekannten Q10-Räume in Raum-IDs.

## Saugleistung oder Wasserfluss lässt sich nicht ändern

Prüfen, ob der Roboter erreichbar ist und ob die offizielle Roborock-Integration den aktuellen Status liefert.

## Diagnose

Für die Fehlersuche kann `roborock_q10.diagnose` mit dem Modus `map` verwendet werden.

Zusätzlich sind Home-Assistant-Logs mit aktiviertem Debug-Logging hilfreich.
