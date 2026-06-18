# hassos-stuff

Home Assistant veci, helpery a blueprinty.

## Obsah

- `blueprints/automation/animus/bazen_filtracia_dynamicka.yaml`
- `blueprints/automation/animus/example_instance_bazen.yaml`
- `blueprints/automation/animus/README.md`

## Pool filtration blueprint

Tento blueprint riesi dynamicku filtraciu bazena v dennych blokoch:

- rano
- obed
- vecer
- tvrdy stop najneskor vecer

Podporuje rezimy:

- `Auto`
- `Eco`
- `Standard`
- `Intenzivny`

V rezime `Auto` vie zohladnit:

- teplotu vody
- UV
- svetlo
- kupanie dnes
- manual boost

Import a priklad pouzitia su v:

- `blueprints/automation/animus/README.md`
