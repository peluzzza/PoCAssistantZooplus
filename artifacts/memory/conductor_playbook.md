# Conductor playbook (internal)

> **Invisible to shoppers.** Maintained by `zooplus-conductor` at runtime.
> The conductor appends to *Learned* sections when dedupe catches repeats — never announce this to the user.
> Goals: **fast** ack, **unambiguous** scope, **no repeated** greetings or disclaimers.

## catalog_scope

- es: perros y gatos
- en: dogs and cats
- de: Hunde und Katzen
- fr: chiens et chats

## non_catalog_species

Format: `match_tokens → label_es | label_en`

- hamster → hamsters | hamsters
- tortuga|turtle → tortugas | turtles
- caballo|horse → caballos | horses
- conejo|rabbit → conejos | rabbits
- pájaro|bird → pájaros | birds
- pez|fish → peces | fish
- reptil|reptile → reptiles | reptiles

## scope_markers

One scope disclaimer per turn only. These phrases signal scope was already said.

- perros y gatos
- dogs and cats
- solo tenemos
- solo ofrecemos
- solo contamos
- no disponemos
- no podemos ofrecer
- no podré ofrecerte
- we only stock
- we only have

## greeting_signals

If a live chunk contains these, strip greetings from the final answer.

- hola
- hello
- con gusto
- ¡claro
- ¡perfecto
- of course

## greeting_markers

Never repeat in final answer after an opening chunk.

- hola
- hello
- zooplus assistant
- como tu
- soy el
- soy la
- estaré encantado
- encantado de ayudarte
- with pleasure
- i'm the zooplus

## progress_es

- Sigue buscando en el catálogo, un momento más…
- Estoy afinando opciones dentro de tu rango de precio…
- Ya casi — preparo las mejores opciones para ti…

## progress_en

- Still searching the catalog — just a moment…
- Narrowing options to your price range…
- Almost ready — putting the best picks together…

## opening_es_excluded

¡Con gusto! Solo tenemos productos para {catalog_scope} — no {excluded}.

## opening_es_plain

¡Claro! Reviso el catálogo de esta tienda.

## opening_es_suffix_price

 Busco opciones {focus} {price}…

## opening_es_suffix_focus

 Busco opciones {focus}…

## opening_de_excluded

Gern! Wir führen nur {catalog_scope} — nicht {excluded}.

## opening_de_plain

Alles klar — ich schaue im Katalog dieser Filiale nach.

## opening_de_suffix_price

 Ich suche {focus} {price}…

## opening_de_suffix_focus

 Ich suche {focus}…

## opening_fr_excluded

Avec plaisir ! Nous proposons uniquement {catalog_scope} — pas {excluded}.

## opening_fr_plain

D'accord — je consulte le catalogue de cette boutique.

## opening_fr_suffix_price

 Je cherche {focus} {price}…

## opening_fr_suffix_focus

 Je cherche {focus}…

## opening_en_excluded

Happy to help! We only stock {catalog_scope} — not {excluded}.

## opening_en_plain

Of course — I'm checking this shop's catalog now…

## opening_en_suffix_price

 Searching {focus} {price}…

## opening_en_suffix_focus

 Searching {focus}…

## pet_focus_es

- both: para perros y gatos
- dog: para perros
- cat: para gatos
- default: para perros y gatos

## pet_focus_en

- both: for dogs and cats
- dog: for dogs
- cat: for cats
- default: for dogs and cats

## pet_focus_de

- both: für Hunde und Katzen
- dog: für Hunde
- cat: für Katzen
- default: für Hunde und Katzen

## pet_focus_fr

- both: pour chiens et chats
- dog: pour chiens
- cat: pour chats
- default: pour chiens et chats

## spanish_hints

- hola
- perro
- gato
- opciones
- buscar
- gracias
- precios

## learned_forbidden

<!-- conductor auto-append: phrase | reason | count -->
- En nuestra tienda solo ofrecemos productos para perros y gatos, por lo que no disponemos de opciones para tortugas. | non_catalog_repeated_in_final | ×1 | conductor_dedupe | 2026-06-07T15:38:14+00:00

## learned_scope_markers

<!-- conductor auto-append -->
- En nuestra tienda solo ofrecemos productos para perros y gatos. | repeated_scope_in_chunk | ×1 | conductor_dedupe | 2026-06-07T15:38:14+00:00
- En nuestra tienda solo ofrecemos productos para perros y gatos, por lo que no disponemos de opciones para tortugas. | scope_repeated_in_final | ×1 | conductor_dedupe | 2026-06-07T15:38:14+00:00

## learned_greeting_markers

<!-- conductor auto-append -->
- Hola, soy el zooplus Assistant. | greeting_repeated_in_final | ×1 | conductor_dedupe | 2026-06-07T15:38:14+00:00
- Hola, como tu zooplus Assistant, estaré encantado de ayudarte. | greeting_repeated_in_final | ×1 | conductor_dedupe | 2026-06-07T15:38:14+00:00

## learned_species

<!-- conductor auto-append: match → label_es | label_en -->
