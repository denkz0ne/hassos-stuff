# hassos-stuff

Home Assistant veci, helpery a blueprinty.

## Obsah

- `blueprints/automation/animus/bazen_filtracia_dynamicka.yaml`
- `blueprints/automation/animus/example_instance_bazen.yaml`
- `blueprints/automation/animus/README.md`

## Pool filtration blueprint

Tento blueprint rieši dynamickú filtráciu bazéna v denných blokoch:

- ráno
- obed
- večer
- najneskoršie večerné vypnutie

Podporuje režimy:

- `Auto`
- `Eco`
- `Standard`
- `Intenzívny`

V režime `Auto` vie zohľadniť:

- teplotu vody
- UV
- svetlo
- kúpanie počas dňa
- manuálny boost

Import a príklad použitia sú v:

- `blueprints/automation/animus/README.md`
