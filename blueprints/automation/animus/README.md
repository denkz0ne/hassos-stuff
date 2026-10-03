# Blueprinty pre HASS

Home Assistant blueprinty v tomto priečinku:

- `bazen_filtracia_dynamicka.yaml`
- `dvere_okna_kontakt_alert.yaml`
- `casove_signaly_multi_event.yaml`
- `setric_svetla.yaml`

## Bazén — dynamická filtrácia

`bazen_filtracia_dynamicka.yaml` riadi filtráciu bazéna v denných blokoch.

Podporuje režimy:

- `Auto`,
- `Eco`,
- `Standard`,
- `Intenzívny`.

## Dvere / okno — kontakt, zvuk a opakovaný alert

`dvere_okna_kontakt_alert.yaml` je univerzálny blueprint pre jeden kontaktný senzor.

Podporuje:

- jeden `binary_sensor` na inštanciu,
- externý `timer` viditeľný aj na dashboarde,
- senzory typu dvere a okno,
- zvuky cez Home Assistant media picker,
- jeden alebo viac `media_player`,
- mobilné notifikácie cez Action selector,
- jednorazový mobilný alert pri zabudnutom otvorení,
- opakovaný zvuk alertu,
- obnovenie pôvodnej hlasitosti prehrávačov,
- nočný režim s vlastným časom.

## Časové znamenia (BETA)

`casove_signaly_multi_event.yaml` je jedna automatizácia pre ľubovoľný počet časových znamení.
Nevyžaduje pomocné skripty ani helpery.

Každé znamenie sa nastavuje cez moderný `object` selector s `multiple: true`.

Podporuje:

- ľubovoľný počet časov v jednej inštancii,
- každý deň / pracovné dni / víkend / vlastné dni,
- dátumové výnimky pre sviatky a pracovné soboty,
- typovú voliteľnú podmienku,
- media picker pre zvuk,
- jeden alebo viac `media_player`,
- vlastnú hlasitosť s obnovením pôvodnej hodnoty,
- opakovanie a pauzu,
- `notify.send_message`,
- AAS vizuálne eventy cez MQTT,
- vlastné HA akcie,
- viac udalostí v rovnakej minúte,
- paralelné vetvy pre audio, AAS, notifikácie a ďalšie akcie.

### AAS vizuálna signalizácia

Podporované semantické eventy:

`ping`, `pohyb`, `zvoncek`, `sprava`, `upozornenie`, `chyba`, `uspech`, `informacia`, `pripomienka`.

Broadcast:

```text
aas/udalost
```

Cielenie na konkrétny node:

```text
aas/udalost/<node_id>
```

Aktuálne node ID:

- `esp-87-bulb`,
- `esp-85-vindriktning`,
- `esphome-117-aura`.

### Vlastné HA akcie

Pole `Doplnkový program` používa natívny Home Assistant Action selector.

Runtime interpreter podporuje:

- bežné `action`/service kroky,
- `target`,
- `data`,
- `delay`,
- aktiváciu `scene`.

Vnorené `choose`, `if`, `repeat` a `parallel` zatiaľ nie sú podporované.

## Šetrič Svetiel — v1.1.2

`setric_svetla.yaml` je jedna blueprint automatizácia pre ľubovoľný počet miestností alebo
samostatných pravidiel.

Každá miestnosť má vlastné:

- zapnutie/vypnutie pravidla; nové pravidlo je predvolene aktívne,
- senzory prítomnosti,
- čas neprítomnosti,
- cieľové entity na vypnutie,
- voliteľnú vlastnú akciu po neprítomnosti,
- voliteľné ranné zhasnutie po východe slnka + offset.

Picker prítomnosti ponúka iba `motion`, `occupancy`, `presence` a `input_boolean`.
Ciele na vypnutie sú zúžené na `light`, `switch`, `group`, `fan`, `media_player`, `humidifier`
a `input_boolean`.

Základná logika:

- `on` = prítomnosť,
- `off` = neprítomnosť,
- `unknown` / `unavailable` = nevypínať,
- všetky senzory musia byť `off`,
- po timeout-e sa použije `homeassistant.turn_off`,
- vlastná akcia sa vykoná iba pri neprítomnosti,
- ranné zhasnutie je jednorazové OFF bez ďalšieho blokovania.

Blueprint nepoužíva timer helpery. Kontroluje stav každých 30 sekúnd a po štarte Home Assistanta.

Podrobný princíp, recovery po reloade/reštarte, obmedzenia a changelog:

- [`setric_svetiel.md`](setric_svetiel.md)

## Import

1. `Nastavenia -> Automatizácie a scény -> Blueprints`
2. `Import blueprint`
3. vlož GitHub URL alebo obsah blueprintu
4. vytvor novú automatizáciu z blueprintu
