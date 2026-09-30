# Šetrič Svetiel

> Aktuálna verzia: **1.1.1**

Šetrič Svetiel je Home Assistant blueprint pre viac miestností v jednej automatizácii.
Jeho úloha je jednoduchá: keď miestnosť zostane prázdna dostatočne dlho, vypne zvolené
svetlá a zariadenia. Bez scén, bez kúziel, bez predstierania, že zabudnutá lampa je životný štýl. 🙂

Blueprint je navrhnutý tak, aby sa jednotlivé miestnosti nastavovali ako samostatné opakovateľné bloky.

## Základný princíp

Každá miestnosť má vlastné:

- zapnutie alebo vypnutie pravidla,
- senzory prítomnosti,
- čas neprítomnosti,
- entity, ktoré sa majú vypnúť,
- voliteľné vlastné akcie po neprítomnosti,
- voliteľné jednorazové ranné zhasnutie po východe slnka.

Prítomnosť používa jednoduchú logiku:

- `on` = niekto je prítomný,
- `off` = miestnosť je prázdna,
- `unknown` alebo `unavailable` = stav nie je dôveryhodný, nič sa nevypína.

Ak je zvolených viac senzorov, miestnosť sa považuje za prázdnu až vtedy, keď sú **všetky**
v stave `off`.

## Nastavenie miestnosti

### Aktívne pravidlo

Hlavný vypínač konkrétneho bloku.

Ak je vypnutý, Šetrič Svetiel túto miestnosť úplne ignoruje.

### Senzory prítomnosti

Picker zámerne ponúka iba entity, ktoré dávajú pre prítomnosť zmysel:

- `binary_sensor` s `device_class: motion`,
- `binary_sensor` s `device_class: occupancy`,
- `binary_sensor` s `device_class: presence`,
- `input_boolean` pre vlastné helpery alebo odvodený stav prítomnosti.

Môže ich byť viac. Stačí, aby jeden z nich hlásil `on`, a miestnosť sa považuje za obsadenú.

Filtrovane sú iba možnosti v editore blueprintu. Runtime logika ostáva jednoduchá:
`on` znamená prítomnosť a `off` neprítomnosť.

### Zhasnúť po neprítomnosti

Určuje, ako dlho musia všetky senzory hlásiť neprítomnosť.

Za začiatok neprítomnosti sa berie najnovší `last_changed` zo zvolených senzorov, teda čas,
keď do `off` prešiel posledný z nich.

Po uplynutí času sa vypnú iba cieľové entity, ktoré ešte nie sú `off`.

### Vypnúť tieto entity

Picker ponúka domény vhodné na jednoduché vypnutie:

- `light`,
- `switch`,
- `group`,
- `fan`,
- `media_player`,
- `humidifier`,
- `input_boolean`.

Vypínanie používa generické `homeassistant.turn_off`, takže jedna miestnosť môže naraz vypnúť
mix podporovaných typov zariadení.

Z pickeru sú zámerne odstránené domény ako `climate`, `remote` a `siren`. Technicky sa vypnúť
dajú, ale pre Šetrič Svetiel skôr zvyšovali šancu na nechcený výber než úžitok.

### Vlastná akcia po neprítomnosti

Voliteľné pole s natívnym Home Assistant Action selectorom.

Vlastná akcia sa spustí **iba vtedy, keď Šetrič Svetiel vypína miestnosť pre neprítomnosť**.
Ranné zhasnutie ju nikdy nespúšťa.

Dynamické akcie vo vnútri opakovateľného objektu sa vykonávajú interným interpreterom.
Verzia 1.1.1 podporuje:

- bežné `action`/service kroky,
- `target`,
- `data`,
- `delay`,
- aktiváciu `scene`.

Vnorené bloky `choose`, `if`, `repeat` a `parallel` sa zatiaľ nevykonávajú.
Pre komplikovanejšiu logiku je najčistejšie zavolať vlastný `script`.

## Ranné zhasnutie

Ranné zhasnutie je úmyselne primitívne.

Ak je zapnuté:

1. Home Assistant určí dnešný východ slnka,
2. pripočíta nastavený čas **Po východe počkať**,
3. v danom okamihu jednorazovo vypne cieľové entity.

Prítomnosť sa pri rannom zhasnutí nekontroluje.
Vlastné akcie sa nespúšťajú.

Po vykonaní sa nič neblokuje. Ak človek, senzor alebo iná automatizácia svetlo neskôr znovu
zapne, Šetrič Svetiel ho kvôli rannému pravidlu druhýkrát nevypína.

Ranné zhasnutie má rozlíšenie kontrolného cyklu, teda maximálne približne 30 sekúnd.

## Kontrolný cyklus a obnova

Blueprint nepoužíva `timer` helpery.

Stav sa kontroluje:

- každých 30 sekúnd,
- okamžite po štarte Home Assistanta.

### Reload automatizácií

Reload automatizácií nemení stav ani `last_changed` prítomnostných senzorov.
Rozbehnutý čas neprítomnosti sa preto dopočíta z ich aktuálneho stavu a pokračuje bez vlastného
timer helpera.

### Reštart Home Assistanta

Po štarte sa miestnosti skontrolujú okamžite.

Ak integrácia senzora obnoví pôvodný stav aj jeho čas zmeny, odpočet sa dopočíta.
Ak zariadenie po štarte nanovo publikuje stav a tým zmení `last_changed`, odpočet sa môže začať
od tohto nového času. Blueprint napriek tomu nezostane visieť na zrušenom `delay` alebo `for`.

Pri rannom zhasnutí je zámerne použitá ochrana proti falošnému vypnutiu po dennom reštarte.
Ak Home Assistant reštartuje až po východe slnka a dnešný východ už nie je možné spoľahlivo
rekonštruovať zo `sun.sun`, ranné zhasnutie sa môže pre daný deň preskočiť. Na ďalší deň funguje
normálne. Je to bezpečnejšie než zhasnúť izbu napríklad na obed len preto, že HA práve nabehol.

## Fail-safe správanie

Ak ktorýkoľvek prítomnostný senzor hlási:

- `unknown`,
- `unavailable`,
- alebo iný stav než `off`,

miestnosť sa nepovažuje za prázdnu.

Blueprint teda radšej raz nezhasne, než aby zhasínal podľa senzora, o ktorom práve nič nevie.

## Odporúčaný test

Na prvý test stačí jedna miestnosť:

1. jeden pohybový senzor,
2. jedna lampa,
3. čas neprítomnosti `00:00:30`,
4. vlastná akcia napríklad jednoduchá notifikácia,
5. ranné zhasnutie zatiaľ vypnuté.

Over:

1. senzor `on` -> nič sa nevypne,
2. senzor `off` -> začne plynúť čas,
3. pred koncom znovu `on` -> vypnutie sa nekoná,
4. znova `off` a počkaj 30 sekúnd -> lampa sa vypne a vykoná sa vlastná akcia,
5. reloadni automatizácie počas odpočtu -> čas sa má dopočítať z `last_changed`.

Ranné zhasnutie sa dá prakticky otestovať až okolo reálneho východu slnka. Na rýchly test je
možné dočasne nastaviť malý offset.

## Changelog

### 1.1.1 — 2026-09-30

- picker prítomnosti obmedzený na `motion`, `occupancy`, `presence` a `input_boolean`,
- picker cieľových entít zúžený na bežné vypínateľné domény,
- pridaná podpora `group` medzi cieľmi,
- z cieľového pickera odstránené `climate`, `remote` a `siren`,
- runtime logika zostala bez zmeny.

### 1.1.0 — 2026-09-30

- názov blueprintu upravený na **Šetrič Svetiel**,
- pridaný hlavný checkbox pre každú miestnosť,
- pridané jednorazové ranné zhasnutie po východe slnka s vlastným offsetom,
- pridané vlastné akcie vykonávané iba po vypnutí z dôvodu neprítomnosti,
- kontrolný cyklus zmenený z 10 na 30 sekúnd,
- pridaná okamžitá kontrola po štarte Home Assistanta,
- doplnené fail-safe a recovery pravidlá,
- doplnená samostatná dokumentácia a verzovanie.

### 1.0.0 — 2026-09-30

- prvá verzia,
- ľubovoľný počet miestností cez `object` selector s `multiple: true`,
- viac prítomnostných senzorov na miestnosť,
- vlastný čas neprítomnosti,
- vypnutie viacerých typov entít,
- interný odpočet bez timer helperov.
