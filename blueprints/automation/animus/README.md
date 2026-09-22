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
Nevyzaduje pomocne skripty ani helpery.

Kazda udalost sa nastavuje cez moderny `object` selector s `multiple: true`.

Podporuje:

- lubovolny pocet casov v jednej instancii blueprintu
- kazdy den / pracovne dni Po-Pi / vikend So-Ne / vlastne dni
- interne datumove vynimky pre sviatok alebo pracovnu sobotu
- typovu volitelnu podmienku:
  - Boolean -> true/false
  - Cislo -> <, <=, =, !=, >=, >
  - Text/stav -> =, !=, obsahuje, neobsahuje, zacina, konci
- media picker pre zvuk
- jeden alebo viac `media_player`
- per-event hlasitost 0-100 % s automatickym obnovenim povodnej hlasitosti kazdeho playera
- pocet prehrati 0-20
- pauzu cez HA duration picker `hh:mm:ss`
- moderne `notify.send_message`
- AAS vizualne eventy cez MQTT
- AAS broadcast na vsetky nody alebo cielenie iba na vybrane ESP
- Vlastne HA akcie priamo cez Action selector v kazdej udalosti
- globalne audio/notify defaulty
- viac udalosti v rovnakej minute
- paralelne vetvy pre audio, AAS, notify a vlastne akcie

### AAS vizualna signalizacia

Blueprint pouziva semanticke AAS eventy:

`ping`, `pohyb`, `zvoncek`, `sprava`, `upozornenie`, `chyba`, `uspech`, `informacia`, `pripomienka`.

Pri volbe `Na vsetkych AAS zariadeniach` publikuje:

```text
aas/udalost
```

Pri volbe `Iba na vybranych ESP` publikuje na:

```text
aas/udalost/<node_id>
```

Aktualne podporovane node ID:

- `esp-87-bulb`
- `esp-85-vindriktning`
- `esphome-117-aura`

Cielenie vyzaduje AAS firmware s podporou per-node topicov.

### Audio a hlasitost

Pred prehratim sa ulozi aktualny `volume_level` kazdeho zvoleneho media playera.
Blueprint nastavi hlasitost udalosti, prehra zvuk(y), pocka na ukoncenie posledneho prehravania
(maximalne 60 s) a nasledne kazdemu playeru obnovi jeho vlastnu povodnu hlasitost.

### Pracovne dni bez Workday helpera

Blueprint pocita bezny rezim autonomne:

- Po-Pi = pracovny den
- So-Ne = vikend / volno

V sekcii `Kalendar bez helperov` mozes pridat datumove vynimky:

- sviatok cez pracovny tyzden -> `Vikend / volno`
- pracovna sobota -> `Pracovny den`

### Vlastne HA akcie

Kazda udalost ma pole `Vlastne HA akcie` s natívnym Home Assistant Action selectorom.

BETA runtime interpreter podporuje:

- bezne action/service kroky s `action`, `target` a `data`
- action bez targetu alebo bez data
- `delay`
- aktivaciu `scene`

Vnorene `choose`, `if`, `repeat` a `parallel` zatial interpreter nevykonava.

### BETA obmedzenia

- casovac ma minutove rozlisenie; sekundy z time pickera sa ignoruju
- `pause = 00:00:00` znamena okamzity dalsi `play_media`
- obnovenie hlasitosti caka na stav playera `playing/buffering`; pri playeri, ktory stav nehlasi spolahlivo, je fallback timeout 60 s

## Import

1. `Nastavenia -> Automatizacie a sceny -> Blueprints`
2. `Import blueprint`
3. vloz URL alebo obsah blueprintu
4. vytvor novu automatizaciu z blueprintu
