# Blueprinty pre HASS

Aktualne blueprinty:

- `bazen_filtracia_dynamicka.yaml`
- `dvere_okna_kontakt_alert.yaml`
- `casove_signaly_multi_event.yaml`

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

## Casove signaly - autonomny multi-event chime & notifier (BETA)

`casove_signaly_multi_event.yaml` je samostatna blueprint automatizacia s lubovolnym poctom casovych udalosti.
Nevyzaduje externe skripty ani helpery.

Kazda udalost sa nastavuje cez moderny `object` selector s `multiple: true`.

Podporuje:

- lubovolny pocet casov v jednej instancii blueprintu
- kazdy den / pracovne dni Po-Pi / vikend So-Ne / vlastne dni
- interne datumove vynimky pre sviatok alebo pracovnu sobotu
- volitelnu podmienku podla stavu lubovolnej entity
- media picker pre zvuk
- Target selector pre media player, notify a svetelne ciele
- pocet prehrati 0-20
- pauzu medzi prehratiami
- moderne `notify.send_message`
- svetla: short flash, long flash, on, off, toggle
- Vlastne HA akcie priamo cez Action selector v kazdej udalosti
- globalne defaulty, ktore moze konkretna udalost prepisat
- viac udalosti v rovnakej minute
- paralelne vetvy pre zvuk, svetlo, notify a vlastne akcie

### Pracovne dni bez Workday helpera

Blueprint pocita bezny rezim autonomne:

- Po-Pi = pracovny den
- So-Ne = vikend / volno

V sekcii `Kalendar bez helperov` mozes pridat datumove vynimky:

- sviatok cez pracovny tyzden -> `Vikend / volno`
- pracovna sobota -> `Pracovny den`

Takto nie je blueprint zavisly od Workday integracie.

### Vlastne HA akcie

Kazda udalost ma priamo pole `Vlastne HA akcie` s natívnym Home Assistant Action selectorom.
Pouziva rovnaky editor akcii ako bezna automatizacia.

V BETA verzii runtime interpreter podporuje:

- bezne integračne/service actions s `action`, `target` a `data`
- action bez targetu alebo bez data
- `delay`
- aktivaciu `scene`

Typicky sem mozes dat napr.:

- ESPHome vlastnu akciu
- efekt konkretnej ziarovky
- mobilnu notifikaciu cez legacy `notify.mobile_app_...`
- MQTT publish
- zapnutie/vypnutie/prepnutie entity
- ovladanie cover, climate, media playera
- aktivaciu sceny

Vnorene flow-control bloky vytvorene v Action editore, napr. `choose`, `if`, `repeat`, `parallel`, zatial BETA interpreter nevykonava. Na bezne HA actions to nema vplyv.

### BETA obmedzenia

- casovac ma minutove rozlisenie; sekundy z time pickera sa ignoruju
- `pause = 0` znamena okamzity dalsi `play_media`; niektore prehravace mozu predosly zvuk prerusit
- natívny `flash` zavisi od podpory konkretneho svetla; specificky ESPHome efekt nastav cez `Vlastne HA akcie`

## Import

1. `Nastavenia -> Automatizacie a sceny -> Blueprints`
2. `Import blueprint`
3. vloz URL alebo obsah blueprintu
4. vytvor novu automatizaciu z blueprintu
