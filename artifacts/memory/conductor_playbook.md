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

## social_help_signals

Capabilities / help asks — route to social lane, never catalog search.

- me puedes ayudar
- puedes ayudarme
- me ayudas
- ayúdame
- necesito ayuda
- can you help
- can you help me
- help me
- how can you help
- what can you do
- kannst du mir helfen
- pouvez-vous m'aider

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
- Por favor, ten en cuenta que en zooplus Assistant solo disponemos de productos para perros y gatos, por lo que no tenemos comida ni accesorios para serpientes de mascotas. | greeting_repeated_in_final | ×1 | conductor_dedupe | 2026-06-08T00:24:59+00:00
- Hola, soy el zooplus Assistant | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T00:25:53+00:00
- Hello! I am the zooplus Assistant | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T00:28:07+00:00
- Hello! I'm the zooplus Assistant | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T00:29:46+00:00
- Hello! I'm the zooplus Assistant | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T21:28:33+00:00
- Hello! I'm the zooplus Assistant for this shop | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T21:31:58+00:00
- Hello! I'm the zooplus Assistant | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T21:34:44+00:00
- Hello! I'm the zooplus Assistant | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T21:35:29+00:00
- I am the zooplus Assistant | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T21:47:51+00:00
- Hello! I am the zooplus Assistant | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T21:50:44+00:00
- Hello! I'm the zooplus Assistant | leading_intro_stripped | ×1 | conductor_dedupe | 2026-06-08T21:50:49+00:00

## learned_species

<!-- conductor auto-append: match → label_es | label_en -->
- serpiente|serpientes → serpientes | serpientes
- some|some → some | some

## learned_social_help

<!-- conductor auto-append: phrase | reason | count -->
- what can you tell me about your services | social_help_detected | ×1 | intent_hints | 2026-06-08T21:47:28+00:00
