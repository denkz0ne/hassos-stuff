# EntityController od danobot — rozbor logiky pre prepis do Home Assistant blueprintu

> Stav rozboru: 2026-09-30  
> Účel: zachytiť **reálne správanie** EntityControllera pred prepisom do natívneho Home Assistant blueprintu.  
> Toto ešte nie je návrh blueprintu. Je to referenčný model, podľa ktorého sa bude blueprint neskôr skladať a testovať.

## 1. Čo bolo preskúmané

Primárny zdroj pravdy je zdrojový kód `danobot/entity-controller`, vetva `master`, release **v9.7.6**, commit:

- `235b4abc4b8cc11604cc5266e82f70d8ea26ed5b`
- release commit z 2024-05-04

Hlavné zdroje:

- https://github.com/danobot/entity-controller
- https://github.com/danobot/entity-controller/blob/master/custom_components/entity_controller/__init__.py
- https://github.com/danobot/entity-controller/blob/master/custom_components/entity_controller/const.py
- https://github.com/danobot/entity-controller/blob/master/custom_components/entity_controller/entity_services.py
- https://github.com/danobot/entity-controller/blob/master/custom_components/entity_controller/services.yaml
- https://github.com/danobot/entity-controller/blob/master/diagram.puml
- https://github.com/danobot/entity-controller/blob/master/CHANGELOG.md
- https://danobot.github.io/ec-docs/

### Dôležité: dokumentácia je staršia než kód

Verejná dokumentácia stále uvádza stable verziu `v6.1.1`, zatiaľ čo `master` obsahuje `v9.7.6`. Preto platí:

1. dokumentácia vysvetľuje pôvodný zámer,
2. zdroják `v9.7.6` rozhoduje o skutočnom správaní,
3. pri rozpore je v tomto dokumente popísané správanie zdrojáku,
4. staré alebo zjavne rozbité časti nebudeme pri prepise do BP kopírovať naslepo.

---

# 2. Základný princíp

EntityController nie je obyčajná automatizácia typu:

`pohyb -> zapni -> počkaj -> vypni`

Je to **konečný stavový automat (FSM)**. Rozhoduje nielen podľa trigger senzora, ale aj podľa:

- aktuálneho stavu ovládaných zariadení,
- toho, či do zariadenia zasiahol používateľ alebo iná automatizácia,
- override entít,
- časového obmedzenia,
- typu senzora,
- timeru,
- night mode,
- stay mode,
- blokovania,
- vlastných ON/OFF stavov entít,
- HA Context ID udalostí.

Hlavná myšlienka je veľmi dobrá: **automatizácia nemá bojovať s manuálnym zásahom používateľa**.

Ak EC zapne svetlo a niekto ho následne manuálne zmení, EC vie prejsť do `blocked` a prestať sa správať ako tvrdohlavý debil, ktorý každých pár sekúnd prepisuje človeka. 😄

---

# 3. Entity a ich úlohy

## 3.1 Sensor entities

Konfigurácia:

- `sensor`
- `sensors`

Sú to vstupné triggre. Nemusia to byť iba motion senzory.

EC sleduje ich **zmenu stavu**, nie zmenu atribútov.

Pri prechode do ON stavu sa spracuje `sensor_on` iba keď je EC v:

- `idle`,
- `active_timer`,
- `blocked`.

V `overridden`, `constrained` a prakticky aj `active_stay_on` sa bežný sensor trigger ignoruje.

---

## 3.2 Control entities

Konfigurácia:

- `entity`
- `entities`

Sú zariadenia, na ktoré EC reálne volá `turn_on` / `turn_off`.

Typicky svetlá, ale princíp nie je viazaný na domain `light`.

Pri `group` používa EC služby `homeassistant.turn_on` / `homeassistant.turn_off`, pretože historicky group nemala vlastný domain service.

---

## 3.3 State entities

Konfigurácia:

- `state_entities`

Toto je jedna z najdôležitejších častí celej logiky.

State entity sa nepoužíva primárne na ovládanie, ale na zisťovanie:

- či je výsledné zariadenie zapnuté,
- či ho niekto manuálne zmenil,
- či má EC prejsť do `blocked`,
- či manuálne vypnutie znamená návrat do `idle`.

Ak `state_entities` nie sú zadané, EC automaticky použije **control entities ako state entities**.

To znamená, že v bežnej konfigurácii sleduje tie isté svetlá, ktoré ovláda.

---

## 3.4 Override entities

Konfigurácia:

- `override`
- `overrides`

Ak je aspoň jedna override entita v ON stave, EC môže prejsť do:

`overridden`

Override predstavuje externú vyššiu prioritu, napríklad:

- vypnutie motion automatiky,
- TV režim,
- návšteva,
- manuálny helper,
- iná logika domácnosti.

Dôležité: `overridden` štandardne **nemení stav control entities**. Iba pozastaví automatické riadenie.

---

## 3.5 Trigger-on-activate / trigger-on-deactivate

Konfigurácia:

- `trigger_on_activate`
- `trigger_on_deactivate`

Ide o pomocné entity, typicky skripty.

Pri aktivácii EC na `trigger_on_activate` volá `turn_on`.

Pri deaktivácii EC na `trigger_on_deactivate` tiež volá `turn_on` — pretože ide skôr o spustenie skriptu než o zapnutie/vypnutie zariadenia.

### Rozpor dokumentácie a zdrojáku

Staršia dokumentácia tvrdí, že trigger entity nedostávajú custom service data.

Zdroják `v9.7.6` ich však **posiela**:

- activation trigger dostáva `service_data`,
- deactivation trigger dostáva `service_data_off`.

Pri porte treba vychádzať zo zdrojáku.

---

# 4. Stavový automat

Aktuálny zdroják používa tieto stavy:

```text
pending
idle
overridden
constrained
blocked
active
  ├─ active_timer
  └─ active_stay_on
```

`active` je nadradený stav s dvoma podstavmi.

---

# 5. Startup

EC po načítaní nezačne okamžite sledovať entity.

Zdroják má:

```text
STARTUP_DELAY = 70 s
```

Po 70 sekundách:

1. načíta konfiguráciu,
2. zostaví zoznam control/state/sensor/override entít,
3. zaregistruje state listenery,
4. nastaví behaviours,
5. pripraví day/night parametre,
6. nastaví časové constraint callbacky,
7. pripraví blokovanie, backoff, sensor type a stay mode,
8. vyhodnotí aktuálny override stav.

Potom:

- ak je override aktívny -> `overridden`,
- inak -> `idle`.

Ak je aktuálny čas mimo povoleného constraint intervalu, `config_times()` navyše naplánuje približne o sekundu prechod do `constrained`.

### Dôsledok startup logiky

Vstup do `idle` má default behaviour `off`.

Teda pri bežnom štarte bez override môže EC po startup delay **vypnúť control entities**.

To nie je iba pasívna inicializácia stavu.

Pri blueprint porte treba toto správanie vedome rozhodnúť — nie automaticky kopírovať.

---

# 6. Default transition behaviours

EC má nastaviteľnú akciu pri vstupe/výstupe zo stavov.

Možnosti:

- `on`
- `off`
- `ignore`

Defaulty v `v9.7.6`:

| Udalosť | Default |
|---|---|
| `on_enter_idle` | `off` |
| `on_exit_idle` | `ignore` |
| `on_enter_active` | `on` |
| `on_exit_active` | `ignore` |
| `on_enter_overridden` | `ignore` |
| `on_exit_overridden` | `ignore` |
| `on_enter_constrained` | `ignore` |
| `on_exit_constrained` | `ignore` |
| `on_enter_blocked` | `ignore` |
| `on_exit_blocked` | `ignore` |

Z toho vyplýva základ:

- vstup do `active` -> zapni,
- vstup do `idle` -> vypni,
- ostatné stavy zariadenie štandardne nemenia.

Custom behaviours môžu tieto akcie predefinovať.

---

# 7. IDLE

`idle` znamená, že EC čaká na trigger a control zariadenia majú byť podľa default behaviour vypnuté.

## Sensor ON v idle

### A. State entities sú OFF

```text
idle -> active
```

EC začne normálny aktívny cyklus.

### B. State entities sú ON a block je povolený

```text
idle -> blocked
```

Logika predpokladá:

> Zariadenie už bolo zapnuté mimo EC. Neberieme mu kontrolu.

### C. State entities sú ON a block je zakázaný

```text
idle -> active
```

EC manuálny stav ignoruje a preberie kontrolu.

---

# 8. ACTIVE

Pri vstupe do nadradeného stavu `active` sa vždy vykoná:

1. uloženie `last_triggered_at`,
2. reset `backoff_count = 0`,
3. výber day/night service parametrov,
4. spustenie timeru,
5. `on_enter_active` behaviour — default `on`,
6. následne rozdelenie do `active_timer` alebo `active_stay_on`.

Výber:

```text
stay == false -> active_timer
stay == true  -> active_stay_on
```

---

# 9. ACTIVE_TIMER

Toto je hlavný pracovný stav.

## 9.1 Sensor ON počas timeru

```text
active_timer -> active_timer
```

Stav sa nemení, ale timer sa resetuje.

Každý ďalší ON trigger teda predlžuje dobu aktivity.

---

## 9.2 Event sensor

Default sensor type je:

```yaml
sensor_type: event
```

Pri event senzore OFF stav nie je podstatný.

Priebeh:

```text
sensor ON
-> active_timer
-> timer beží
-> ďalší sensor ON resetne timer
-> timer vyprší
-> idle
-> control entities OFF
```

---

# 10. Duration sensor

Konfigurácia:

```yaml
sensor_type: duration
```

Legacy alternatíva v kóde:

```yaml
sensor_type_duration: true
```

Duration senzor má význam ON počas aktivity a OFF po skončení aktivity.

EC pri ňom vyžaduje, aby nastali **obe podmienky**:

- timer už vypršal,
- senzor už nie je ON.

Platí princíp „čo nastane neskôr“.

## Scenár A — timer vyprší ako prvý

```text
sensor stále ON
-> timer vyprší
-> EC zostáva active_timer
-> expires_at = "pending sensor"
-> sensor neskôr OFF
-> idle
```

## Scenár B — sensor OFF ako prvý

```text
sensor OFF
-> timer ešte beží
-> EC zostáva active_timer
-> timer neskôr vyprší
-> idle
```

---

# 11. sensor_resets_timer

Ak je:

```yaml
sensor_resets_timer: true
```

potom OFF udalosť duration senzora timer **resetne**.

Tým vznikne minimálny čas svietenia ešte po skončení detekcie.

Priebeh:

```text
motion ON
-> timer
-> motion OFF
-> timer sa spustí odznova
-> timer vyprší
-> idle
```

---

# 12. Backoff timer

Voliteľná funkcia:

```yaml
backoff: true
backoff_factor: 1.1
backoff_max: 300
```

Pri prvom spustení sa použije normálny `delay`.

Pri každom resete timeru:

```text
nový_delay = predchádzajúci_delay × backoff_factor
```

Výsledok sa zaokrúhli na 2 desatinné miesta a oreže na `backoff_max`.

Default:

- factor `1.1`
- max `300 s`

Backoff count sa resetuje pri novom vstupe do `active`.

Backoff teda neznamená exponenciálne predlžovanie medzi všetkými cyklami. Predlžuje iba **opakované retriggery jedného aktívneho cyklu**.

---

# 13. Manuálna zmena control/state entity počas active_timer

Toto je jadro priority logiky EC.

State listener ignoruje vlastné zmeny, ktoré vytvoril EC. Ak však zmena prišla zvonka, vyhodnotí ju.

## 13.1 State entity sa manuálne vypne

Ak už state entities nie sú ON:

```text
active_timer -> idle
```

EC teda rešpektuje ručné vypnutie.

Timer sa zruší.

---

## 13.2 State entity je ON alebo sa významne zmení a block je povolený

```text
active_timer -> blocked
```

To platí aj pri významnej zmene atribútov — napríklad manuálnej zmene jasu — ak daný atribút nie je ignorovaný.

Význam:

> Používateľ prevzal kontrolu. EC sa stiahne.

---

## 13.3 State entity je ON a block je zakázaný

Stav ostáva `active_timer`, ale timer sa resetuje.

EC teda manuálny zásah nepovažuje za dôvod na blokovanie.

---

# 14. BLOCKED

`blocked` znamená, že EC dočasne **neovláda control entities**, pretože vyhodnotil externý/manuálny zásah.

Do blocked sa vstupuje napríklad keď:

- sensor trigger príde, ale svetlo už bolo zapnuté,
- počas aktívneho cyklu používateľ zmení stav alebo významný atribút svetla,
- službou sa manuálne vyvolá block.

Default behaviour blocked stavu je `ignore`, teda zariadenie sa nechá tak.

---

## 14.1 Sensor ON počas blocked

EC vykoná self-transition:

```text
blocked -> blocked
```

To spôsobí opätovné vykonanie `on_enter_blocked`.

Ak je nastavený `block_timeout`, timeout sa prakticky obnoví.

---

## 14.2 State entity sa vypne

State listener v blocked zavolá `enable`.

Ak sú state entities OFF:

```text
blocked -> idle
```

Tým sa blok automaticky skončí.

---

## 14.3 block_timeout

Voliteľné:

```yaml
block_timeout: <sekundy>
```

Po timeout-e sa EC pokúsi blok uvoľniť.

Ak je state entity stále ON:

### Event sensor

```text
blocked -> active
```

### Duration sensor a sensor je ON

```text
blocked -> active
```

### Duration sensor a sensor je OFF

```text
blocked -> idle
```

Teda po timeout-e EC znovu prehodnotí, či má pokračovať v automatickom cykle alebo skončiť.

---

## 14.4 disable_block

```yaml
disable_block: true
```

vypína automatický blocked mechanizmus.

Pri zapnutom `disable_block` externá zmena state entity počas timeru namiesto blocked iba resetuje timer.

---

# 15. OVERRIDDEN

Override je samostatná vyššia priorita.

Ak override entita prejde do ON a EC je v podporovanom stave:

```text
-> overridden
```

Pri vstupe sa defaultne nič nezapína ani nevypína.

## Keď posledný override zhasne

EC sa rozhoduje podľa aktuálneho stavu zariadenia a senzora.

### State entities OFF

```text
overridden -> idle
```

### State entities ON + event sensor

```text
overridden -> active
```

### State entities ON + sensor aktuálne ON

```text
overridden -> active
```

### State entities ON + duration sensor + sensor OFF

```text
overridden -> idle
```

Zmysel je: ak zariadenie po skončení override stále logicky patrí do aktívneho cyklu, EC ho nechá dobehnúť cez timer. Ak nie, ukončí ho.

---

# 16. CONSTRAINED — časové obmedzenie

Ak sú nastavené obe hodnoty:

```yaml
start_time:
end_time:
```

EC je aktívny iba vo vnútri intervalu.

Mimo intervalu prechádza do:

```text
constrained
```

`constrain` je definovaný zo `*`, teda môže prerušiť prakticky ľubovoľný stav.

Podporované formáty času v zdrojáku:

```text
HH:MM:SS
YYYY-MM-DD HH:MM:SS
sunrise
sunset
sunrise +/- HH:MM:SS
sunset +/- HH:MM:SS
```

Zdroják obsahuje aj debug syntax typu `now + N`.

Interval správne rieši prechod cez polnoc.

Príklad:

```text
22:00 -> 06:00
```

je chápaný ako interval cez ďalší deň.

---

## 16.1 Koniec povoleného intervalu

Pri `end_time`:

```text
ľubovoľný stav -> constrained
```

Ak sa opúšťa `active`, zruší sa aktívny timer.

Default `on_enter_constrained = ignore`, takže constrained sám o sebe štandardne nevypína zariadenie.

---

## 16.2 Začiatok povoleného intervalu

Pri `start_time`:

- ak je state entity ON a block je povolený -> `blocked`,
- inak sa použije `enable`.

`enable` z constrained vedie:

- do `idle`, ak override nie je aktívny,
- do `overridden`, ak override aktívny je.

---

# 17. Night mode

Night mode nie je to isté ako time constraint.

Constraint určuje:

> či EC smie fungovať.

Night mode určuje:

> aké parametre má použiť, keď funguje.

Konfigurácia night mode obsahuje vlastné:

- `start_time`,
- `end_time`,
- `delay`,
- `service_data`,
- `service_data_off`.

Ak niektoré service parametre v night mode chýbajú, preberajú sa z day mode.

Pri každom novom vstupe do `active` sa zavolá `prepare_service_data()` a podľa aktuálneho času sa vyberie day alebo night sada.

Night mode teda môže mať napríklad:

- kratší timer,
- nižší jas,
- inú farbu,
- iné vypínacie parametre.

---

# 18. Stay mode

Konfigurácia:

```yaml
stay_mode: true
```

alebo runtime služby:

- `enable_stay_mode`
- `disable_stay_mode`

Pri ďalšom vstupe do `active`:

```text
active -> active_stay_on
```

V `active_stay_on` sa zariadenie nevypne po normálnom timere.

Keď state entity manuálne prejde do OFF:

```text
active_stay_on -> idle
```

### Dôležitý detail runtime služby

`enable_stay_mode` a `disable_stay_mode` iba zmenia boolean `stay`.

Neprenášajú okamžite už bežiaci cyklus medzi `active_timer` a `active_stay_on`.

Teda zmena sa plnohodnotne prejaví až pri ďalšom vstupe do nadradeného `active`.

---

# 19. Service data

Day mode:

```yaml
delay:
service_data:
service_data_off:
```

Night mode môže mať vlastné hodnoty.

Pri aktivácii control entity:

```text
<domain>.turn_on
```

s `service_data`.

Pri deaktivácii:

```text
<domain>.turn_off
```

s `service_data_off`.

Rovnaké dáta v aktuálnom zdrojáku dostávajú aj trigger-on-activate/deactivate entity, iba pri trigger entitách sa vždy volá `turn_on`.

---

# 20. ON/OFF stavové reťazce

Default ON hodnoty:

```text
on
playing
home
True
```

Default OFF hodnoty:

```text
off
idle
paused
away
False
```

Existujú konfiguračné skupiny:

```text
sensor_states_on / sensor_states_off
override_states_on / override_states_off
state_states_on / state_states_off
control_states_on / control_states_off
state_strings_on / state_strings_off
```

`state_strings_on/off` pridávajú hodnoty globálne.

### Dôležitý implementačný detail

Predikáty typu:

```text
is_sensor_off
is_state_entities_off
```

v skutočnosti často neoverujú explicitný OFF zoznam. Overujú skôr:

> nenašla sa žiadna entita v ON stave.

Preto neznámy stav môže byť v niektorých vetvách prakticky považovaný za „nie ON“.

Na druhej strane callback duration senzora reaguje na OFF udalosť iba vtedy, keď nový stav patrí do `SENSOR_OFF_STATE`.

To je jemný, ale podstatný rozdiel.

---

# 21. Ignorovanie vlastných zmien — Home Assistant Context

Od v9 EC používa Home Assistant Context API, aby nereagoval na svoje vlastné service calls.

Pri vlastnom zásahu vytvorí Context ID v tvare približne:

```text
ec_<hash>_<uuid>
```

State listener ignoruje každý event, ktorého context ID začína:

```text
ec_
```

Dôležitý dôsledok:

EC neignoruje iba vlastnú konkrétnu inštanciu, ale prakticky **udalosti všetkých EntityController inštancií**, pretože filter je globálny prefix `ec_`.

To zabraňuje tomu, aby sa dva EC controllery navzájom blokovali svojimi service callmi.

---

# 22. ignored_event_sources

`ignored_event_sources` sa v aktuálnom zdrojáku nepoužíva ako zoznam entity_id.

Hodnoty sa používajú ako **regex prefixy Context ID**.

Ak context udalosti zodpovedá niektorému patternu, state change sa úplne ignoruje.

Pri blueprint porte musíme túto funkciu interpretovať opatrne; UI by nemalo predstierať, že ide o obyčajný entity selector.

---

# 23. state_attributes_ignore

Ak sa nezmení hlavný stav entity, ale iba atribúty, EC porovná staré a nové atribúty.

Atribúty uvedené v:

```yaml
state_attributes_ignore:
```

z porovnania odstráni.

Ak po odstránení ignorovaných atribútov ostanú dictionary rovnaké, udalosť sa zahodí.

Ak sa zmení iný atribút, zmena je významná a v `active_timer` môže vyvolať blocked logiku.

Typické použitie:

- automatická zmena `brightness`,
- `color_temp`,
- transition atribúty,
- integrácie typu circadian lighting.

---

# 24. Manuálne služby EntityControllera

Reálne registrované služby podľa `const.py` + `entity_services.py`:

## `activate`

- z `idle` alebo `blocked` vynúti `active`,
- v `active_timer` resetne timer,
- z blocked teda vie násilne prevziať riadenie.

## `clear_block`

Ak je stav `blocked`, zavolá logiku `block_timer_expires`.

Nie je to slepé `blocked -> idle`. Znovu vyhodnotí sensor/state stav a môže skončiť aj v `active`.

## `enable_block`

Ak je EC práve `active_timer`, pokúsi sa prejsť do `blocked`.

Prechod je možný iba keď:

- state entity je ON,
- blocking nie je disabled.

## `enable_stay_mode`

Nastaví `stay = true`.

## `disable_stay_mode`

Nastaví `stay = false`.

## `set_night_mode`

Za behu upraví start/end night mode.

Špeciálne hodnoty:

- `now`
- `constraint`

Ak sa nezadá ani start ani end, obe hodnoty nastaví na `00:00:00`.

### Rozpor v `services.yaml`

`services.yaml` stále obsahuje staré názvy:

- `set_stay_on`
- `set_stay_off`

ale aktuálny Python registruje:

- `enable_stay_mode`
- `disable_stay_mode`

Pre port berieme Python ako pravdu.

---

# 25. Prechodová tabuľka — skrátená referenčná mapa

| Aktuálny stav | Trigger | Podmienka | Nový stav / efekt |
|---|---|---|---|
| `pending` | startup | override OFF | `idle` |
| `pending` | startup | override ON | `overridden` |
| `*` | constraint začne | — | `constrained` |
| `idle` | sensor ON | state OFF | `active` |
| `idle` | sensor ON | state ON + block enabled | `blocked` |
| `idle` | sensor ON | state ON + block disabled | `active` |
| `active_timer` | sensor ON | — | reset timer |
| `active_timer` | timer expires | event sensor | `idle` |
| `active_timer` | timer expires | duration + sensor OFF | `idle` |
| `active_timer` | timer expires | duration + sensor ON | ostáva active, čaká na sensor OFF |
| `active_timer` | duration sensor OFF | timer už expired | `idle` |
| `active_timer` | duration sensor OFF | timer beží | čaká na timer |
| `active_timer` | duration sensor OFF | `sensor_resets_timer` | reset timer |
| `active_timer` | external state change | state OFF | `idle` |
| `active_timer` | external state change | state ON + block enabled | `blocked` |
| `active_timer` | external state change | state ON + block disabled | reset timer |
| `blocked` | sensor ON | block enabled | re-enter `blocked`, obnov timeout |
| `blocked` | state OFF | — | `idle` |
| `blocked` | block timeout | event sensor | `active` |
| `blocked` | block timeout | duration + sensor ON | `active` |
| `blocked` | block timeout | duration + sensor OFF | `idle` |
| `overridden` | posledný override OFF | state OFF | `idle` |
| `overridden` | posledný override OFF | state ON + event sensor | `active` |
| `overridden` | posledný override OFF | state ON + sensor ON | `active` |
| `overridden` | posledný override OFF | duration + sensor OFF | `idle` |
| `constrained` | constraint skončí | state ON + block enabled | `blocked` |
| `constrained` | constraint skončí | override ON | `overridden` |
| `constrained` | constraint skončí | inak | `idle` |
| `active_stay_on` | state OFF | — | `idle` |

---

# 26. Veci, ktoré sú v zdrojáku podozrivé alebo historicky prerastené

Tieto body treba pri porte riešiť vedome. Nie sú to vlastnosti, ktoré treba automaticky reprodukovať.

## 26.1 Dokumentácia je na v6.1.1, kód na v9.7.6

Časť dokumentácie opisuje staršie správanie.

---

## 26.2 `diagram.puml` nie je úplne aktuálny

Diagram napríklad začína priamo v Idle, zatiaľ čo aktuálny kód má `pending` + 70 s startup delay.

Niektoré podmienky pre blocking tiež nezodpovedajú poslednému kódu.

---

## 26.3 `services.yaml` má staré názvy stay služieb

Python a YAML service popisy si odporujú.

---

## 26.4 Dokumentácia trigger entít tvrdí niečo iné než kód

Docs tvrdia, že trigger entities nedostávajú service data. Aktuálny kód ich posiela.

---

## 26.5 `control_states_on/off` vyzerajú ako mŕtva konfigurácia

Kód ich naplní do `CONTROL_ON_STATE` / `CONTROL_OFF_STATE`, ale hlavná rozhodovacia logika state entities používa `STATE_ON_STATE`.

Pri state entities, ktoré defaultne kopírujú control entities, sa teda aj tak používa `state_states_on`, nie `control_states_on`.

V porte to netreba reprodukovať bez praktického dôvodu.

---

## 26.6 Stay mode stále pri vstupe do Active spustí timer

`on_enter_active()` spúšťa timer ešte pred rozdelením na `active_timer` / `active_stay_on`.

Pre `active_stay_on` pritom nie je normálny timer transition definovaný.

To pôsobí ako historický artefakt a potenciálny zdroj chýb.

Blueprint by mal stay režim implementovať priamo bez zbytočného timeru.

---

## 26.7 Override počas `active_stay_on`

Callback override zmenu akceptuje cez kontrolu nadradeného `active`, ale transition `override` je explicitne definovaný pre `active_timer`, nie pre `active_stay_on`.

To môže skončiť invalid transition/MachineError.

Pri BP porte treba definovať jednoznačné správanie.

---

## 26.8 Constraint callback vykonáva behaviour duplicitne

`end_time_callback()` explicitne volá `on_enter_constrained` behaviour a potom vykoná transition do constrained, ktorý ho zavolá znovu.

Podobný problém je pri výstupe z constrained.

Pri `ignore` je to neviditeľné, ale pri `on/off` môže ísť action dvakrát.

Toto je skôr bug než feature.

---

## 26.9 Komentár pri skončení constraintu nesedí s default Idle behaviour

Komentár tvrdí, že pri vypnutom blockingu môže EC prejsť do idle a nechať zapnutú entitu tak.

Lenže `on_enter_idle` má default `off`, takže výsledkom je normálne vypnutie.

Pri porte sa treba riadiť zamýšľanou logikou, nie týmto rozporným komentárom.

---

## 26.10 Vlastný Context prefix ignoruje aj ostatné EC inštancie

Filter je `ec_`, nie presné ID aktuálnej inštancie.

Je to pravdepodobne zámer na zabránenie cross-blockingu, ale pri BP treba rozhodnúť, či chceme:

- ignorovať iba vlastnú automation inštanciu,
- alebo všetky inštancie rovnakého blueprintu.

---

# 27. Čo je podľa mňa jadro EntityControllera, ktoré musí prežiť port do BP

Bez týchto častí by už nešlo o prepis EC, ale iba o ďalší motion-light blueprint:

1. viac sensor entít,
2. viac control entít,
3. state entities oddelené od control entities,
4. event aj duration sensor režim,
5. reset timeru pri ďalšom triggeri,
6. voliteľný reset timeru po OFF duration senzora,
7. rešpektovanie manuálneho OFF,
8. `blocked` pri externom zásahu,
9. voliteľné vypnutie block mechanizmu,
10. block timeout,
11. override entities,
12. časové constrainty,
13. night/day parametre,
14. stay mode,
15. vlastné aktivačné/deaktivačné akcie,
16. ochrana pred reakciou na vlastné service calls,
17. ignorovanie vybraných atribútových zmien,
18. vlastné ON/OFF stavy tam, kde majú reálny význam,
19. manuálny „activate / clear block / enable block“ ekvivalent alebo rozumná BP náhrada,
20. jednoznačné recovery správanie po reload/reštarte HA.

---

# 28. Čo nemusíme kopírovať 1:1

Pri blueprint verzii nemá zmysel zachovávať historické implementačné čudá iba preto, že tam sú:

- Python `transitions` knižnicu,
- 70-sekundový startup delay,
- staré debug time hacky,
- mŕtve config parametre,
- duplicitné transition callbacks,
- staré service názvy,
- invalid transition edge cases,
- interné EntityController entity atribúty iba kvôli debug UI,
- chyby vzniknuté historickým vrstvením verzií.

Cieľ portu má byť:

> zachovať rozhodovaciu logiku a priority EntityControllera, ale implementovať ich natívnym, čitateľným a predvídateľným spôsobom v aktuálnom Home Assistante.

---

# 29. Návrh ďalšieho kroku

Ďalší krok už nemá byť písanie YAML naslepo.

Najskôr treba z tejto referencie vytvoriť **BP model správania**:

1. definovať minimálny počet interných stavov, ktoré BP reálne potrebuje,
2. rozhodnúť, či stav odvodiť z entít alebo držať v helperi,
3. namapovať každý EC transition na HA trigger/choose/wait logiku,
4. vyriešiť Context/self-event ochranu natívnym HA spôsobom,
5. oddeliť kompatibilné správanie od historických EC bugov,
6. až potom vytvoriť blueprint inputy a UI.

Tento dokument je referenčný kontrakt pre tieto kroky.
