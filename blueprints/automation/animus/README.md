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

## Casove signaly - multi-event chime & notifier (BETA)

`casove_signaly_multi_event.yaml` je jedna automatizacia s lubovolnym poctom casovych udalosti.

Kazda udalost ma vlastny formular cez moderny `object` selector s `multiple: true`.

Podporuje:

- lubovolny pocet casov v jednej instancii blueprintu
- kazdy den / Workday / non-Workday / vikend / vlastne dni
- volitelny per-event `input_boolean` alebo `binary_sensor` guard
- media picker pre zvuk
- jeden alebo viac `media_player`
- pocet prehrati 0-20
- pauzu medzi prehratiami
- moderne `notify` entity cez `notify.send_message`
- legacy notify sluzby, napr. `notify.mobile_app_telefon`
- svetla: short flash, long flash, on, off, toggle
- samostatny Visual/ESP script
- samostatny Extra script pre lubovolnu vlastnu Home Assistant logiku
- globalne defaulty, ktore moze jednotliva udalost prepisat
- viac udalosti v rovnakej minute

### Workday

Ak vyberies Workday `binary_sensor`, rezimy pracovny/nepracovny den respektuju jeho stav a teda aj sviatky podla konfiguracie Workday integracie.

Ak Workday senzor nevyberies, blueprint pouzije fallback:

- Po-Pi = pracovny den
- So-Ne = nepracovny den

Rezim `Vikend` je vzdy striktne Sobota + Nedela.

### Extra a Visual script

Per-event script je univerzalny escape hatch pre cokolvek, co nema zmysel natvrdo zabudovat do blueprintu.
Blueprint ho spusta cez `script.turn_on` a odovzda mu premenne:

- `event_name`
- `event_time`
- `title`
- `message`
- `day_mode`
- Extra script navyse dostane `is_workday`

Script nemusi mat tieto polia deklarovane, ale ak ich pridas ako Fields, budu sa pohodlnejsie testovat cez UI.

### BETA obmedzenia

- casovac ma zatial minutove rozlisenie; sekundy z time pickera sa ignoruju
- `pause = 0` znamena okamzity dalsi `play_media`; niektore prehravace mozu predosly zvuk prerusit
- uplne lubovolna per-event action sequence je riesena cez `script.*`, pretoze dynamicke vykonanie celeho action selectora ulozeneho v jednom object zazname nie je v HA script syntax spolahlivy mechanizmus
- native `flash` zavisi od podpory konkretneho svetla; pre ESPHome efekty pouzi Visual/ESP script

## Import

1. `Nastavenia -> Automatizacie a sceny -> Blueprints`
2. `Import blueprint`
3. vloz URL alebo obsah blueprintu
4. vytvor novu automatizaciu z blueprintu
