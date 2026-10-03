# Šetrič Svetiel

> Aktuálna verzia: **1.1.3**

Šetrič Svetiel je Home Assistant blueprint pre viac miestností v jednej automatizácii.
Jeho úloha je jednoduchá: keď miestnosť zostane prázdna dostatočne dlho, vypne zvolené
svetlá a zariadenia. Bez scén, bez kúziel, bez predstierania, že zabudnutá lampa je životný štýl. 🙂

Blueprint je navrhnutý tak, aby sa jednotlivé miestnosti nastavovali ako samostatné opakovateľné bloky.

## Zdroj a aktualizácie

Stabilný zdroj blueprintu je:

`https://github.com/denkz0ne/hassos-stuff/blob/main/blueprints/automation/animus/setric_svetla.yaml`

Rovnaká adresa je zapísaná aj v `blueprint.source_url`. V popise blueprintu sa verzia zapisuje vo
formáte `**Version**: x.y.z`, aby bola čitateľná používateľovi a použiteľná aj pre externé
kontroléry aktualizácií.

Pri ďalších vydaniach zostáva cesta k YAML súboru rovnaká. Nová verzia sa publikuje do `main`,
nie do novej URL.

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

Ak pravidlo vypneš, Šetrič Svetiel túto miestnosť úplne ignoruje.

Pre spätnú kompatibilitu platí: ak staršia uložená konfigurácia pole `enabled` vôbec nemá,
runtime ho vyhodnotí ako `true`.

Home Assistant však aktuálne nepodporuje `default` priamo na vnorenom poli `object` selectora.
Preto sa predvolená poloha checkboxu pri vytváraní nového záznamu nedá korektne vynútiť cez
`fields.enabled.default`. Verzia 1.1.2 sa o to pokúsila a výsledkom bola neplatná schema; 1.1.3 túto
chybu opravuje.

### Senzory prítomnosti

Picker zámerne ponúka iba entity, ktoré dávajú pre prítomnosť zmysel:

- `binary_sensor` s `device_class: motion`,
- `binary_sensor` s `device_class: occupancy`,
- `binary_sensor` s `device_class: presence`,
- `input_boolean` pre vlastné helpery alebo odvodený stav prítomnosti.

Môže ich byť viac. Stačí, aby jeden z nich hlásil `on`, a miestnosť sa považuje za obsadenú.

Filtrované sú iba možnosti v editore blueprintu. Runtime logika ostáva jednoduchá:
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
Verzia 1.1.3 podporuje:

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

30-sekundový kontrolný cyklus je zámerný. Pri dynamickom počte miestností v jednom `object`
selectore je jednoduchší a predvídateľnejší než globálne počúvanie všetkých `state_changed`
udalostí v Home Assistante. Timeout sa pritom stále počíta z reálneho `last_changed`, takže
polling neurčuje začiatok neprítomnosti; iba okamih najbližšej kontroly.

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

### 1.1.3 — 2026-10-03

- opravená neplatná schema z 1.1.2; odstránené nepodporované `default` z vnoreného `object` poľa,
- pridaný stabilný `blueprint.source_url` smerujúci na vetvu `main`,
- verzia v popise zjednotená na marker `**Version**: x.y.z`,
- runtime fallback `enabled -> true` zostáva zachovaný,
- funkčná logika vypínania sa nemení.

### 1.1.2 — 2026-10-03

- pokus nastaviť `Aktívne pravidlo` ako predvolene zapnuté priamo vo vnorenom `object` poli,
- táto verzia obsahovala nepodporovaný kľúč `default` v `fields.enabled` a bola nahradená 1.1.3,
- 30-sekundový kontrolný cyklus zostal zachovaný.

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
