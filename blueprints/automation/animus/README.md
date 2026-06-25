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
- zvuk otvorenia, zatvorenia a alertu sa prehrava priamo cez vybrany `media_player`
- alert sa vie opakovat az do zatvorenia
- po alerte sa obnovi povodna hlasitost prehravaca
- podporuje nocny rezim s vlastnym casom od-do
- telefonne notifikacie su volitelne

## Import

1. `Nastavenia -> Automatizacie a sceny -> Blueprints`
2. `Import blueprint`
3. vloz URL alebo obsah blueprintu
4. vytvor novu automatizaciu z blueprintu
