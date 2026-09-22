# hassos-stuff

Home Assistant veci, helpery a blueprinty.

## Obsah

- `blueprints/automation/animus/bazen_filtracia_dynamicka.yaml`
- `blueprints/automation/animus/dvere_okna_kontakt_alert.yaml`
- `blueprints/automation/animus/casove_signaly_multi_event.yaml`
- `blueprints/automation/animus/example_instance_bazen.yaml`
- `blueprints/automation/animus/README.md`

## Blueprinty

### Pool filtration

Dynamicka filtracia bazena v dennych blokoch s rezimami `Auto`, `Eco`, `Standard` a `Intenzivny`.

### Dvere / okno alert

Kontaktovy senzor, zvuky, timer, nocny rezim a mobilne akcie.

### Casove signaly - autonomny multi-event chime & notifier

Jedna blueprint instancia s lubovolnym poctom casovych udalosti. Kazda moze mat vlastne dni, typovu podmienku, zvuk, hlasitost s obnovenim povodnej hodnoty, opakovanie a duration pauzu, notify, AAS MQTT signalizaciu pre vsetky alebo vybrane ESP a vlastne Home Assistant akcie.

Podrobnosti, import a poznamky k beta verzii su v:

- `blueprints/automation/animus/README.md`
