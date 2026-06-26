# Blueprinty pre HASS

Aktualne blueprinty:

- `bazen_filtracia_dynamicka.yaml`
- `dvere_okna_kontakt_alert.yaml`

## Bazen - dynamicka filtracia s dennymi blokmi

`bazen_filtracia_dynamicka.yaml` riesi dynamicku filtraciu bazena v dennych blokoch:

- rano
- obed
- vecer
- najneskorsie vecerne vypnutie

Podporuje rezimy:

- `Auto`
- `Eco`
- `Standard`
- `Intenzivny`

## Dvere/okno - kontakt, zvuk a opakovany alert

`dvere_okna_kontakt_alert.yaml` je univerzalny blueprint pre jeden kontaktovy senzor.

- jedna instancia = jeden `binary_sensor`
- kazda instancia pouziva vlastny externy `timer`
- timer sa vybera v instancii blueprintu a je viditelny na dashboarde
- kontaktovy senzor je filtrovany na `door` a `window`
- zvuky sa vyberaju cez Home Assistant media picker
- zvuk otvorenia, zatvorenia a alertu sa prehrava cez jeden alebo viac vybranych `media_player`
- mobilne notifikacie sa nastavuju cez action picker
- mobilny alert pri zabudnutom otvoreni sa posiela iba raz
- periodicky sa opakuje iba zvuk alertu
- po alerte sa obnovi povodna hlasitost prehravacov
- podporuje nocny rezim s vlastnym casom od-do
- mobilne notifikacie su volitelne

## Import

1. `Nastavenia -> Automatizacie a sceny -> Blueprints`
2. `Import blueprint`
3. vloz URL alebo obsah blueprintu
4. vytvor novu automatizaciu z blueprintu
