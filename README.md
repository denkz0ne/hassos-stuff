# hassos-stuff

Home Assistant veci, helpery a blueprinty.

## Obsah

- `blueprints/automation/animus/bazen_filtracia_dynamicka.yaml`
- `blueprints/automation/animus/dvere_okna_kontakt_alert.yaml`
- `blueprints/automation/animus/casove_signaly_multi_event.yaml`
- `blueprints/automation/animus/setric_svetla.yaml`
- `blueprints/automation/animus/setric_svetiel.md`
- `blueprints/automation/animus/example_instance_bazen.yaml`
- `blueprints/automation/animus/README.md`

## Blueprinty

### Pool filtration

Dynamická filtrácia bazéna v denných blokoch s režimami `Auto`, `Eco`, `Standard` a `Intenzívny`.

### Dvere / okno alert

Kontaktný senzor, zvuky, timer, nočný režim a mobilné akcie.

### Časové znamenia

Jedna blueprint inštancia s ľubovoľným počtom časových znamení. Každé môže mať vlastné dni,
podmienku, zvuk, hlasitosť s obnovením pôvodnej hodnoty, opakovanie, prestávku, textové
oznámenie, AAS signalizáciu a doplnkový program.

### Šetrič Svetiel — v1.1.0

Jedna blueprint inštancia pre ľubovoľný počet miestností. Každá miestnosť má vlastné senzory
prítomnosti, čas neprítomnosti a zoznam entít na vypnutie. Voliteľne vie po neprítomnosti
spustiť vlastnú akciu a jednorazovo ráno zhasnúť po východe slnka + offset.

Podrobný princíp, nastavenie, recovery správanie a changelog:

- `blueprints/automation/animus/setric_svetiel.md`

Prehľad všetkých blueprintov a import:

- `blueprints/automation/animus/README.md`
