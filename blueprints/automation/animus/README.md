# Blueprinty pre HASS

Aktuálny blueprint pre bazén:

- `bazen_filtracia_dynamicka.yaml`

## Čo robí

- drží filter zapnutý iba počas aktívnych časových okien
- podporuje režimy `Auto`, `Eco`, `Standard`, `Intenzívny`
- má prehľadné sekcie vstupov priamo v UI
- helpery sú voliteľné
- večer nikdy nenechá filter bežať po čase `Najneskoršie vypnutie`

## Import

1. `Nastavenia -> Automatizácie a scény -> Blueprints`
2. `Import blueprint`
3. vlož obsah súboru `bazen_filtracia_dynamicka.yaml`
4. vytvor novú automatizáciu z blueprintu

## Príklad inštancie

Pozri:

- `example_instance_bazen.yaml`
