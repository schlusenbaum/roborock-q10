# Installation

## Voraussetzungen

Vor der Installation der Q10-Erweiterung muss die offizielle Home-Assistant-Roborock-Integration installiert und eingerichtet sein.

Der Roborock Q10 muss dort bereits als Vacuum-Entity verfügbar sein.

## HACS

1. HACS öffnen.
2. **Integrationen** öffnen.
3. Das Repository als Custom Repository hinzufügen.
4. Als Typ **Integration** auswählen.
5. **Roborock Q10** installieren.
6. Home Assistant neu starten.

## Manuelle Installation

Das Verzeichnis der Integration muss nach `/config/custom_components/roborock_q10/` kopiert werden.

Enthalten sind unter anderem:

```text
__init__.py
manifest.json
config_flow.py
sensor.py
select.py
button.py
switch.py
diagnostics.py
services.yaml
```

Danach Home Assistant neu starten.

## Nach der Installation

Die Q10-Integration wird über die Home-Assistant-Konfiguration eingerichtet und mit der bereits vorhandenen Roborock-Vacuum-Entity verknüpft.

Die Integration erzeugt dabei kein zweites physisches Roborock-Gerät.
