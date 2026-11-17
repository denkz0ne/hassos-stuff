# Blueprinty pre HASS

Home Assistant blueprinty v tomto priečinku:

- `bazen_filtracia_dynamicka.yaml` — **v1.0.0**
- `dvere_okna_kontakt_alert.yaml` — **v2.0.1**
- `casove_signaly_multi_event.yaml` — **v1.0.0**
- `setric_svetla.yaml` — **v1.2.0**

## Aktualizácie a verzovanie

Všetky blueprinty v tejto kolekcii používajú rovnaký princíp:

- `blueprint.source_url` smeruje na stabilný súbor vo vetve `main`,
- verzia je uvedená na začiatku popisu vo formáte `**Version**: x.y.z`,
- funkčné zmeny zvyšujú minor verziu,
- opravy bez zmeny funkcií zvyšujú patch verziu,
- breaking zmeny zvyšujú major verziu.

`source_url` je natívna metadata Home Assistanta a je dôležitá pre opätovný import a kontrolu
zdroja. Textový `Version` marker je navyše ľahko čitateľný používateľom aj externým nástrojom,
ktoré porovnávajú lokálnu a vzdialenú verziu blueprintu.

Pri publikovaní novej verzie sa nemení cesta k YAML súboru. Stabilná URL zostáva na `main`, aby
existujúce importy neostali visieť na starej vetve alebo commite.

## Bazén — dynamická filtrácia

`bazen_filtracia_dynamicka.yaml` riadi filtráciu bazéna v denných blokoch.

Podporuje režimy:

- `Auto`,
- `Eco`,
- `Standard`,
- `Intenzívny`.

## Univerzálny sledovač stavu — v2.0.1

`dvere_okna_kontakt_alert.yaml` je jeden blueprint pre ľubovoľný počet nezávislých sledovačov.

Každý záznam má vlastné:

- entitu z domén `binary_sensor`, `switch`, `light` alebo `sensor`,
- cieľový stav vrátane `unknown` alebo `unavailable`,
- odklad pred začiatkom upozorňovania (0 = okamžite),
- media playery a zvuky pri vstupe, počas upozorňovania a po zmene stavu,
- interval opakovania zvuku a celkový čas upozorňovania,
- voliteľné AAS eventy pri začiatku, zmene stavu a vypršaní času.

Telegram a vlastné akcie sa nastavujú v troch spoločných Action poliach: začiatok,
zmena sledovaného stavu a uplynutie celkového času. Akcie môžu používať
`monitor_name_value` a `monitor_state_value`, aby správa pomenovala konkrétny
záznam. Každý sledovač beží nezávisle; ukončenie jedného nemení ostatné.

Blueprint počúva udalosti zmeny stavu HA a v akciách spracuje iba zvolené entity.
Pre import použi stabilnú URL na `main` z metadát blueprintu.

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

## Šetrič Svetiel — v1.2.0

`setric_svetla.yaml` je jedna blueprint automatizácia pre ľubovoľný počet miestností alebo
samostatných pravidiel.

Každá miestnosť má vlastné:

- zapnutie/vypnutie pravidla,
- senzory prítomnosti,
- čas neprítomnosti,
- cieľové entity na vypnutie,
- voliteľnú vlastnú akciu po neprítomnosti,
- voliteľné ranné zhasnutie po východe slnka + offset.

Ak staršia uložená konfigurácia nemá pole `enabled`, runtime ju považuje za aktívnu. Home Assistant
aktuálne nepodporuje `default` priamo na vnorenom poli `object` selectora, preto sa default prepínača
nevynucuje neplatnou schémou.

Picker prítomnosti ponúka iba `motion`, `occupancy`, `presence` a `input_boolean`.
Ciele na vypnutie sú zúžené na `light`, `switch`, `group`, `fan`, `media_player`, `humidifier`
a `input_boolean`.

Základná logika:

- `on` = prítomnosť,
- `off` = neprítomnosť,
- `unknown` / `unavailable` = nevypínať,
- všetky senzory musia byť `off`,
- timeout začne až pri súčasnej neprítomnosti a aktívnom cieli,
- jeho začiatok je neskorší z momentu neprítomnosti a momentu aktivácie cieľa,
- po timeout-e sa použije `homeassistant.turn_off`,
- vlastná akcia sa vykoná iba pri neprítomnosti,
- ranné zhasnutie je jednorazové OFF bez ďalšieho blokovania.

Blueprint nepoužíva timer helpery. Kontroluje stav každých 30 sekúnd a po štarte Home Assistanta.

Podrobný princíp, recovery po reloade/reštarte, obmedzenia a changelog:

- [`setric_svetiel.md`](setric_svetiel.md)

## Import

1. `Nastavenia -> Automatizácie a scény -> Blueprints`
2. `Import blueprint`
3. vlož stabilnú GitHub URL zo súboru v `main`
4. vytvor novú automatizáciu z blueprintu
