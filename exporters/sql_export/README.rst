*************************************
Eksport til Actual State SQL database
*************************************

Indledning
==========
Denne eksport laver et dags-dato udtræk af MO og afleverer det i en SQL database.

For at opnå den nødvendige afviklingshastighed, tilgår eksporten data direkte fra
LoRa hvor det er muligt at lave bulk udtræk, baseret på den kendte datamodel for
OS2MO behandles de udtrukne data så SQL eksporten får et udseende som svarer til
det man finder i MO.

Tabellerne er for den praktiske anvendeligheds skyld ikke 100% normaliserede, der
vil således for alle klasser altid være både en reference til primærnøglen for
klassen plus en tekstrepræsentation, så det er muligt at aflæse tabellen uden at
skulle foretage et join mod tabellen ``klasser`` for alle opslag.

Implementerigen er foretaget ved hjælp af værktøjet SQLAlchemy, som sikrer at
det er muligt at aflevere data til en lang række forskellige databasesystemer,
det er desuden muligt at køre hele eksporten mod en flad SQLite fil som muliggør
eksportering helt uden en kørende databaseserver.

Konfiguration
=============

For at anvende eksporten er det nødvendigt at oprette et antal nøgler i
`settings.json`:

 * ``exporters.actual_state.manager_responsibility_class``: UUID på det lederansvar,
   som angiver at en leder kan nedarve sin lederrolle til enheder dybere i
   organisationen.
 * ``exporters.actual_state.type``: Typen af database, i øjeblikket understøttes
   `SQLite` og `MS-SQL`, flere kan tilføjes efter behov. For typen `SQLite` kan
   brugernavn, password og host være tomme felter.
 * ``exporters.actual_state.user``:  Brugernavn for sql bruger.
 * ``exporters.actual_state.password``: Password til sql bruger.
 * ``exporters.actual_state.db_name``: Navnet på databasen.
 * ``exporters.actual_state.host``: Hostnavn på SQL-serveren.


.. _Modellering:

Modellering
===========

Langt hovedparten af de data som eksporteres kan betragtes som rene rådata,
der er dog nogle få undtagelser, hvor værdierne er fremkommet algoritmisk:

 * ``enheder.organisatorisk_sti``: Angiver den organisatoriske sti for en enhed
   beregnet ved at gå baglæns gennem enhedstræet og tilføje et `\\`-tegn mellem
   hver enhed. Eksempel: `Basildon Kommune\\Kunst & Kultur\\Musiktilbud\\Øvelokaler`.
 * ``enheder.fungerende_leder``: I MO er en leder modeleret som en
   organisationfunktion som sammenkæder en person med en enhed. Der er ikke noget
   krav om at alle enheder har en lederfunktion pegende på sig, og der vil derfor
   være enheder som ikke figurerer i tabellen ``ledere``. For disse enheder er det
   muligt algoritmisk at bestemme en leder ved at gå op i træet indtil der findes
   en leder med passende lederansvar. Dette felt indeholder resultatet af denne
   algoritme.
 * ``adresser.værdi``: For alle adressetyper, undtaget DAR adresser, er dette
   felt taget direkte fra rådata. For DAR-adresser, er rådata en UUID og ikke en
   tekststreng, i dette tilfælde indeholder dette felt resultatet af et opsalg mod
   DAR, og den egentlige rådata (UUID'en) befinder sig i feltet ``dar_uuid``.
 * ``engagementer.primærboolean``: Beregnes ved at iterere hen over alle engagementer
   for en bruger, det engagement som har det højeste `scope` på sin primærklasse
   vil blive markeret som primær, alle andre vil blive markeret som ikke-primært.

Eksporterede tabeller
=====================

Eksporten producerer disse tabeller, indholdet af de enkelte tabeller gennemgås
systematisk i det følgende afsnit.

 * ``facetter``
 * ``klasser``
 * ``brugere``
 * ``enheder``
 * ``adresser``
 * ``engagementer``
 * ``roller``
 * ``tilknytninger``
 * ``orlover``
 * ``it_systemer``
 * ``it_forbindelser``
 * ``ledere``
 * ``leder_ansvar``


facetter
--------

 * ``uuid``: Facettens uuid, primærnøgle for tabellen.
 * ``bvn``: Brugervendt nøgle for facetten.

Facetter i MO har ikke nogen titel.

klasser
--------

 * ``uuid``: Klassens uuid, primærnøgle for tabellen.
 * ``bvn``: Brugervendt nøgle for klassen.
 * ``titel``: Klassens titel, det er denne tekst som vil fremgå af MOs frontend.
 * ``facet_uuid``: Reference til primærnøglen i tabellen ``facetter``.
 * ``facet_bvn``: Den brugervendte nøgle som knytter sig til klassens facet.


brugere
--------
 * ``uuid``: Brugerens uuid, primærnøgle for tabellen.
 * ``fornavn``: Brugerens fornavn.
 * ``efternavn``:  Brugerens efternavn.
 * ``cpr``:  Brugerens cpr-nummer.


enheder
--------
 * ``uuid``: Enhedens uuid, primærnøgle for tabellen.
 * ``navn`` Enhedens navn.
 * ``forældreenhed_uuid``: Reference til primærnøglen for forælderenheden.
 * ``enhedstype_uuid``: Enhedstypen, reference til primærnøglen i tabellen
 * ``enhedstype_titel``: Titel på enhedstypens klasse.
   ``klasser``.
 * ``enhedsniveau_uuid``: Enhedsniveau, dette felt anvendes normalt kun af kommuner,
   som anvender SD som lønsystem. reference til primærnøglen i tabellen
   ``klasser``.
 * ``enhedsniveau_titel``: Titel på klassen for enhedsniveau.
 * ``organisatorisk_sti``: Enhedens organisatoriske placering, se afsnit om
   `Modellering`_.
 * ``leder_uuid``: Reference til primærnøglen for det lederobjet som er leder af
   enheden. Informationen er teknisk set redundant, da den også fremkommer ved et
   join til tabellen ``ledere``, men angives også her som en bekemmelighed.
 * ``fungerende_leder_uuid``: Reference til primærnøglen for nærmeste leder af
   enheden. Hvis enheder har en leder, vil dette være det samme som `leder`. Feltet
   er et afledt felt og findes ikke i rådata, se afsnit om `Modellering`_.


adresser
--------

Adresser er i MO organisationfunktioner med funktionsnavnet ``Adresse``.

 * ``uuid``: Adressens (org-funk'ens) uuid, primærnøgle for tabellen
 * ``bruger_uuid``: Reference til primærnøglen i tabellen ``brugere``. Hvis adressen
   er på en enhed, vil feltet være blankt.
 * ``enhed_uuid``: Reference til primærnøglen i tabellen ``enheder``.  Hvis adressen
   er på en bruger, vil feltet være blankt.
 * ``værdi``: Selve adressen, hvis adressen er en DAR-adresse, vil dette felt
   indeholde en tekstrepræsentation af adressen.
 * ``dar_uuid``: DAR-uuid'en som liger bag opslaget som fremgår af ``værdi_tekst``.
   Blankt hvis ikke adressen er en DAR-adresse.
 * ``adressetype_uuid``: Adressetypen, reference til primærnøglen i tabellen
   ``klasser``.
 * ``adressetype_scope``: Adressens overordnede type (omfang), eksempelvis Telefon
   eller P-nummer.
 * ``adressetype_titel``: Titlen på adressetypens klasse.
 * ``synlighed_uuid``: Synlighedstype, reference til primærnøglen i tabellen
   ``klasser``.
 * ``synlighed_titel``: Titlen på synlighedstypens klasse.


engagementer
--------

Engagementer er i MO organisationfunktioner med funktionsnavnet ``Engagement``.

 * ``uuid``: Engagementets (org-funk'ens) uuid, primærnøgle for tabellen.
 * ``bruger_uuid``: Reference til primærnøglen i tabellen ``brugere``. 
 * ``enhed_uuid``: Reference til primærnøglen i tabellen ``enheder``. 
 * ``bvn``: Engagementets brugervendte nøgle. Dette vil i de fleste tilfælde
   være ansættelsesnummeret i lønsystemet.
 * ``arbejdstidsfraktion``: Angiver den registrerede arbejdstidsfraktion for
   engagementet.
 * ``engagementstype_uuid``: Engagementstypen, reference til primærnøglen i tabellen
   ``klasser``.
 * ``engagementstype_titel``: Titlen på engagementstypeklassen.
 * ``primærtype_uuid``: Engagementets primærtype, reference til primærnøglen i
   tabellen ``klasser``.
 * ``primærtype_titel``: Titlen på primærtypetypeklassen.
 * ``stillingsbetegnelse_uuid``: Engagementets stillingsbetegnelse, reference til
   primærnøglen i tabellen ``klasser``.
 * ``job_function_titel``: Titlen på klassen for stillingsbetegnelse.
 * ``primær_boolean``: Boolean som angiver om engagementet er brugerens primære
   engagement, se afsnit om beregnede felter
 * ``udvidelse_1``: Første af 10 fritekstfelter på MOs engagementer
 * ....
 * ``udvidelse_10``: Sidste af 10 fritekstfelter på MOs engagementer


roller
--------

Roller er i MO organisationfunktioner med funktionsnavnet ``Rolle``.

 * ``uuid``: Rollens (org-funk'ens) uuid, primærnøgle for tabellen.
 * ``bruger_uuid``: Reference til primærnøglen i tabellen ``brugere``. 
 * ``enhed_uuid``: Reference til primærnøglen i tabellen ``enheder``. 
 * ``rolletype_uuid``: Rolletypen, reference til primærnøglen i tabellen
   ``klasser``.
 * ``rolletype_titel``: Titlen på klassen for rolletypen.

   
tilknytninger
--------

Tilknytninger er i MO organisationfunktioner med funktionsnavnet ``Tilknytning``.

 * ``uuid``: Tilknytningens (org-funk'ens) uuid, primærnøgle for tabellen.
 * ``bvn``: Tilknytningens brugervendte nøgle.
 * ``bruger_uuid``: Reference til primærnøglen i tabellen ``brugere``. 
 * ``enhed_uuid`: Reference til primærnøglen i tabellen ``enheder``. 
 * ``tilknytningstype_uuid``: Tilknytningstypen, reference til primærnøglen i tabellen
   ``klasser``.
 * ``tilknytningstype_text``: Titlen på klassen for tilknytningstypen.


orlover
--------

Orlover er i MO organisationfunktioner med funktionsnavnet ``Orlov``.

 * ``uuid``:  Orlovens (org-funk'ens) uuid, primærnøgle for tabellen.
 * ``bvn``: Brugervendt nøgle for orloven.
 * ``bruger_uuid``:  Reference til primærnøglen i tabellen ``brugere``. 
 * ``orlovstype_text``: Titlen på klasse for orlovstypen.
 * ``orlovstype_uuid``: Orlovstypen, reference til primærnøglen i tabellen
   ``klasser``.

it_systemer
--------
 * ``uuid``: IT-systemets uuid, primærnøgle for tabellen.
 * ``navn``: IT-systemets navn.

it_forbindelser
---------------

IT-forbindelser er i MO organisationfunktioner med funktionsnavnet ``IT-system``.

IT-forbindeler dækker over en sammenkædningen mellem et IT-system og enten en enhed
eller en bruger. Hvis forbindelsen er til en bruger, vil sammenkædningen indeholde
brugerens brugernavn i det pågældende system. Hvis forbindelsen er til en enhed, skal
den tolkes i betydningen, at dette IT-system er i anvendelse i den pågældende enhed,
i dette tilfælde vil der normalt ikke være brugernavn på forbindelsen.

 * ``uuid``: IT-forbindelsens (org-funk'ens) uuid, primærnøgle for tabellen.
 * ``it_system_uuid``: Reference til primærnøglen i tabellen ``it_systemer``
 * ``bruger_uuid``: Reference til primærnøglen i tabellen ``brugere``.  Hvis
   it-forbindelsen er på en enhed, vil feltet være blankt.
 * ``enhed_uuid``: Reference til primærnøglen i tabellen ``enheder``. 
 * ``brugernavn``: Brugerens brugernavn i IT-systemet. Normalt blank for forbindelser
   til enheder.

ledere
--------
 * ``uuid``: Lederrollens (org-funk'ens) uuid, primærnøgle for tabellen.
 * ``bruger_uuid``: Reference til primærnøglen i tabellen ``brugere``.
 * ``enhed_uuid``: Reference til primærnøglen i tabellen ``enheder``.
 * ``ledertype_titel``: Titlen på klassen for ledertypen.
 * ``ledertype_uuid``: Klassen for ledertypen, reference til primærnøglen i tabellen
   ``klasser``.
 * ``niveautype_titel``: Titlen på klassen for lederniveau.
 * ``niveautype_uuid``: Klassen for lederniveau, reference til primærnøglen i
   tabellen ``klasser``.

leder_ansvar
------------

Lederansvar er i MO ikke et selvstændigt objekt, men er modelleret som en liste af
klasser som tilknyttes en lederrolle.

 * ``id``: Arbitrært løbenummer, denne tabel har ikke har nogen naturlig primærnøgle.
 * ``leder_uuid``: Reference til primærnøglen i tabellen ``ledere``.
 * ``lederansvar_uuid``: Klassen for lederansvar, reference til primærnøglen i tabellen
   ``klasser``.
 * ``lederansvar_titel``: Titlen på klassen for lederansvar.
