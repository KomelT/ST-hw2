# Navodila

V programskem jeziku Python implementirajte spletni strežnik, ki deluje po poenostavljeni različici protokola HTTP. Uporabite priložene datoteke. Pri tem je nujno, da strežnik implementirate sami in da ne uporabljate funkcij, modulov in paketov z izjemo tistih, kateri so že uvoženi v datoteko `server.py`. Nalogo v celoti implementirajte v tej datoteki in jo oddajte v [sistem za avtomatično ocenjevanje](https://lem-grader.fri.uni-lj.si/grader).

Svojo implementacijo preizkusite na enotskih (unit) testih. V datoteki `tests.py` boste našli začetni skelet in nekaj testov. Pisanje dodatnih testov je opcijsko in se ne bo ocenjevalo, je pa to daleč najboljši način za preverjanje pravilnosti delovanja vaše kode. Pozor: testi pobrišejo vsebino podatkovne baze. Svetujem t. i. [TDD pristop](https://en.wikipedia.org/wiki/Test-driven_development#Test-driven_development_cycle), kjer najprej napišete test, nato pa implementirate funkcionalnost, da se test uspešno izvede.

Vsako prepisovanje bo strogo sankcionirano: naloge, ki bodo vsebovale neavtorske elemente, bodo ocenjene z 0 točkami. To velja tako za prepisovalca kot za tistega, ki da nalogo v prepis. (In glede na pravila predmeta to tudi pomeni, da sta oba udeleženca prepisovanja s predmetom zaključila.)

## Specifikacije naloge

Strežnik naj podpira:

- Izključno zahtevke po protokolu HTTP/1.1. To pomeni, da je polje `host` v zaglavju zahtevka obvezno;
- Izključno metodi `GET` in `POST`. Pri zahtevkih po metodi POST je v zaglavju zahtevka obvezno polje `content-length`, ki vam pove velikost telesa zahtevka (tj. parametrov). Nekaj primerov zahtevkov najdete na tej [spletni strani](https://www.tutorialspoint.com/http/http_requests.htm).

Strežnik naj obdeluje tako **statične** kot tudi **dinamične** vsebine. Pri statičnih vsebinah gre za strežbo datotek iz datotečnega sistema (znotraj imenika `www-data`), pri dinamičnih pa za implementacijo preproste spletne aplikacije, ki hrani podatke o študentih v podatkovni bazi.

## Odgovori HTTP

Čeprav protokol HTTP podpira [precej različnih kod odgovorov](https://www.tutorialspoint.com/http/http_status_codes.htm), naj vaš strežnik podpira le te, ki so navedene spodaj. Za lažjo predstavo si lahko primere odgovorov ogledate t[ej spletni strani](https://www.tutorialspoint.com/http/http_responses.htm).

### 200 OK

V kolikor strežnik prejme veljaven zahtevek, naj vrne odgovor s kodo `200 OK`. Za pripravo zaglavja odgovora uporabite podano predlogo v spremenljivki `HEADER_RESPONSE_200`.

### 301 Moved Permanently

V kolikor mora strežnik odjemalca preusmeriti na drugo stran, uporabite odgovor s kodo `301 Moved Permanently`. Primer takega zaglavja najdete [na Wikipediji](https://en.wikipedia.org/wiki/HTTP_301). Pomembno je, da v takem odgovoru pravilno nastavite vrstico odgovora ter zaglavje, medtem ko je telo odgovora lahko poljubno (a odjemalcu-človeku še vedno razumljivo).

### 400 Bad request

V kolikor strežnik prejme zahtevek, ki s specifikacijami strežnika ni skladen, naj vrne odgovor `400 Bad request`. Pomembno je, da v takem odgovoru pravilno nastavite vrstico odgovora ter zaglavje, medtem ko je telo odgovora lahko poljubno (a odjemalcu-človeku še vedno razumljivo).

### 404 Not found

V kolikor strežnik prejme zahtevek za vir, ki ne obstaja, naj vrne napako `404 Not found`. Odgovor pripravite s pomočjo spremenljivke `RESPONSE_404`.

### 405 Method not allowed

V kolikor strežnik prejme zahtevek po neveljavni metodi, naj vrne napako `405 Method not allowed`. Pomembno je, da v takem odgovoru pravilno nastavite vrstico odgovora ter zaglavje, medtem ko je telo odgovora lahko poljubno (a odjemalcu-človeku še vedno razumljivo).

## Strežba statičnih vsebin

Pri strežbi statičnih vsebin gre za strežbo datotek iz direktorija `www-data`.

### Metode

Statične vsebine se naj strežejo po metodah `GET` in `POST`. Na zahtevke po drugih metodah naj strežnik odgovori z napako `405`.

### Polji `content-length` in `content-type`

V zaglavju odgovora naj strežnik pravilno nastavi tako velikost vsebine (polje `content-length`), kot tudi tip vsebine (polje `content-type`). Pri nastavljanju slednjega si lahko pomagate s funkcijo `guess_type` iz paketa `mimetypes`. V kolikor funkcija `guess_type` ne uspe ugotoviti pravilnega tipa vsebine (tj. vrne None), ga ročno nastavite na `application/octet-stream`.

### Razčlenjevanje parametrov

Predpostavite, da bodo parametri zahtevka (bodisi v naslovu URL pri zahtevkih GET bodisi v telesu pri zahtevkih POST) vedno zakodirani po [pravilu, ki velja za protokol HTTP](https://www.tutorialspoint.com/http/http_url_encoding.htm). Pri zahtevkih POST lahko predpostavite, da bo content-type zahtevka vedno nastavljen na `application/x-www-form-urlencoded`.

Parametre dekodirajte z uporabo vgrajene funkcije `unquote_plus` iz paketa `urllib.parse`.

### Strežba datotek in direktorijev

Kadar odjemalec zahteva URI, ki kaže na dejansko datoteko ali direktorij, zahtevan vir pošljite odjemalcu in nastavite kodo odgovora `200`. Če zahtevani vir (datoteka ali mapa) ne obstaja, vrnite napako `404`.

Pri strežbi statičnih datotek morate biti posebej pozorni na t. i. zaključno poševnico (angl. trailing slash `/`) v naslovu URI kot sledi.

### Primeri brez zaključne poševnice

Ob zahtevkih na vire, ki v URI nimajo zaključne poševnice, naj strežnik postopa sledeče; kot primer imejmo zahtevek na URI `http://localhost[:port]/dir/test`.

1. Če obstaja datoteka `test` (znotraj direktorija `dir`), jo pošljite odjemalcu. Pri ugotavljanju obstoja datoteke si pomagajte s funkcijo `isfile`.
2. Če obstaja direktorij `test` (znotraj direktorija `dir`), odjemalca preusmerite na naslov `http://localhost[:port]/dir/test/` tj. v naslov dodajte zaključno poševnico (`/`, angl. trailing slash). Odjemalca preusmerite tako, da mu vrnete odgovor `301`, v zaglavje odgovora pa dodajte polje `Location`. Pri ugotavljanju ali direktorij obstaja, uporabite funkcijo `isdir`.

### Primeri z zaključno poševnico

Ob zahtevkih, ko odjemalec zahteva vir z zaključno poševnico, naj strežnik postopa sledeče; kot primer ponovno vzemimo zahtevek na URI `http://localhost[:port]/dir/test/`.

1. Če obstaja datoteka `index.html` (znotraj direktorija `dir/test/`), odjemalcu servirajte vsebino omenjene datoteke tj. datoteko `/dir/test/index.html` in nastavite kodo odgovora `200`.
2. Če v direktoriju `dir/test/` datoteke `index.html` ni, odjemalcu servirajte kodo `200`, v telesu odgovora pa navedite seznam datotek, ki se v direktoriju nahajajo. Seznamu datotek vedno dodajte še zapis .., ki kaže na mesto višje v direktorijski strukturi.

Pri pripravi seznama datotek si pomagajte s spremenljivkama `DIRECTORY_LISTING` ter `FILE_TEMPLATE`. Prva določa okvirni dokument HTML, ki podaja seznam datotek in direktorijev, drugo pa uporabite za prikaz posamezne datoteke oz. direktorija. Datoteke in direktorije iz posamezne lokacije pridobite s pomočjo funkcije `listdir`. Pred izpisom zapise uredite po naraščajočem abecednem vrstnem redu (od A-Z). V nadaljevanju je podan primer odgovora za zahtevek `GET` na naslov `http://localhost/listing/`.

```http
HTTP/1.1 200 OK
content-type: text/html
content-length: 669
connection: Close

<!DOCTYPE html>
<html lang="en">
<meta charset="UTF-8">
<title>Directory listing: /listing/</title>

<h1>Contents of /listing/:</h1>

<ul>
  <li><a href='..'>..</li>
  <li><a href='a.html'>a.html</li>
  <li><a href='dir'>dir</li>
  <li><a href='file_1.txt'>file_1.txt</li>
  <li><a href='file_10.txt'>file_10.txt</li>
  <li><a href='file_2.txt'>file_2.txt</li>
  <li><a href='file_3.txt'>file_3.txt</li>
  <li><a href='file_4.txt'>file_4.txt</li>
  <li><a href='file_5.txt'>file_5.txt</li>
  <li><a href='file_6.txt'>file_6.txt</li>
  <li><a href='file_7.txt'>file_7.txt</li>
  <li><a href='file_8.txt'>file_8.txt</li>
  <li><a href='file_9.txt'>file_9.txt</li>
</ul>
```

## Strežba dinamičnih vsebin

Implementirajte dinamično aplikacijo, preko katere lahko vnašate in berete podatke o študentih, ki so vpisani na predmet Spletne tehnologije.
Podatkovna baza (že implementirano)

Aplikacija deluje s pomočjo že implementirane podatkovne baze. Ta sestoji iz datoteke, ki hrani podatke, in iz dveh funkcij, s pomočjo katerih beremo in pišemo v datoteko.

S funkcijo `save_to_db(first(str), last(str))` dodajamo zapise v podatkovno bazo, s funkcijo `read_from_db(criteria(dict))` pa zapise iz podatkovne baze beremo. (Ne pozabite: enotski testi pobrišejo vsebino podatkovne baze.)

Klic `save_to_db("Janez", "Novak")` bo v podatkovno bazo dodal zapis. Hkrati bo zapisu (študentu) tudi priredil enolično številko.

Interno je zapis o posameznem študentu realiziran s pomočjo slovarja, ki ima tri ključe: `number`, `first` in `last`. Ključ `number` je enolično število, ključa `first` in `last` pa zaporedoma predstavljata ime in priimek študenta. Primer zapisa je podan spodaj.

```python
student = {"number": 1, "first": "Janez", "last": "Novak"}
```

Funkcija `read_from_db(criteria(dict))` vrne seznam takih slovarjev. Funkcijo lahko pokličete z opcijskim argumentom tipa `dict`, s katerim lahko dodatno omejimo rezultate. Na primer, spodnji klic bo iz podatkovne baze pridobil vse zapise, kjer sta zaporedoma ime in priimek študenta Janez Novak.

```python
students = read_from_db({"first": "Janez", "last": "Novak"})
# students je seznam zapisov
```

Kot kriterij lahko podate poljubno kombinacijo ključev `number`, `first` in `last`.

### Oblikovanje aplikacije (že implementirano)

Izgled (HTML in CSS) je definiran v datotekah `app_list.html`, `app_add.html` ter `user_style.css`. Teh datotek ne spreminjajte.

### Implementacija aplikacije

Aplikacija naj deluje na spodaj navedenih (navideznih) naslovih URL. (Naslovu pravimo navidezen, saj datoteke `app-add`, `app-index` ter `app-json` ne obstajajo, čeprav z vidika odjemalca morda izgleda nasprotno.)

### Dodajanje zapisov v bazo

URL: `http://localhost[:port]/app-add`

Na tem naslovu URL sprejemate zahtevke po metodi POST. Zahtevek mora nujno vsebovati 2 parametra: `first`, ki vsebuje ime, in `last`, ki vsebuje priimek študenta.

V kolikor sta oba parametra prisotna, dodajte zapis v PB, vrnite kodo `200` in v telesu odgovora vrnite vsebino datoteke `app_add.html`.

Če kateri od parametrov manjka, vrnite odgovor `400`, če metoda zahtevka ni ustrezna, vrnite odgovor `405`.

### Branje in filtriranje v formatu HTML

URL `http://localhost[:port]/app-index`

Na tem naslovu URL sprejemate zahtevke le po metodi GET, sicer vrnite ustrezno napako. Če je zahtevek brez parametrov, iz baze preberite vse zapise in pripravite odgovor s kodo `200`.

Rezultat prikažite s pomočjo predloge v datoteki `user_list.html`. Pri izpisu vsebine datoteke `user_list`.html zamenjajte niz `{{STUDENTS}}` s seznamom študentov, ki ga oblikujete s pomočjo spremenljivke `ROW_TEMPLATE`. Namreč, vsak študent naj bo predstavljen z eno vrstico v tabeli.

```python
TABLE_ROW = """

<tr>
    <td>%d</td>
    <td>%s</td>
    <td>%s</td>
</tr>
"""
```

Spremenljivka `ROW_TEMPLATE` vsebuje tri mesta, na katera boste zapisali podatke o študentu: pri izpisu zamenjajte `%d` s parametrom number, prvi `%s` s parametrom first in drugi `%s` s parametrom last.

Zahtevek GET lahko vsebuje parametre, s katerimi dodatno omejimo izpis. Parametri so lahko trije: `number`, `first` in `last`. Če je katerikoli od teh parametrov nastavljen, ga uporabite za filtriranje seznama študentov. Tako naj npr. poizvedba GET na naslov `http://localhost[:port]/app-index?first=Janez` vrne vse študente, katerih ime je Janez.

### Branje in filtriranje v formatu JSON

URL `http://localhost[:port]/app-json`

Na tem naslovu URL sprejemate zahtevke le po metodi GET, sicer vrnite ustrezno napako. Če je zahtevek brez parametrov, iz baze preberite vse zapise in pripravite odgovor s kodo `200`.

Rezultat prikažite kot sporočilo v formatu JSON. Pri tem si pomagajte z modulom `json` in funkcijo `json.dumps(object);` podatke, ki jih dobite iz podatkovne baze lahko neposredno podate funkciji, denimo `json.dumps(read_from_db())`.

Rezultat vrnite v telesu odgovora. Pri vračanju rezultata v formatu JSON je pomembno, da nastavite pravilen `content-type` na `application/json`. Primer odgovora je podan spodaj.

```http
HTTP/1.1 200 OK
content-type: application/json
content-length: 256
connection: Close

[
  {
    "number": 1,
    "first": "Janez",
    "last": "Novak"
  },
  {
    "number": 2,
    "first": "Marija",
    "last": "Novak"
  },
  {
    "number": 3,
    "first": "Cirila",
    "last": "Novak"
  }
]
```

## Ostale zahteve

Ne pozabite, pri implementaciji ne smete uporabiti funkcij, modulov ali paketov, razen tistih, ki so že uvoženi v datoteko `server.py` (`mimetypes`, `pickle`, `socket`, `os.path.isdir`, `urllib.parse.unquote_plus` in `json`) ali tistih, katere boste spisali sami.

Pri pisanju testov te omejitve ni: nekateri testi že uporabljajo zunanjo knjižnico [Requests](http://docs.python-requests.org/) za pošiljanje zahtevkov in razčlenjevanje odgovorov.

Ocenjevanje bo potekalo s pomočjo integracijskih testov na enak način kot je zapisano v datoteki `tests.py`: za vsako zahtevano funkcionalnost bo napisan integracijski test, ki bo strežniku poslal zahtevek in preveril ustreznost odgovora.

Vaš strežnik bo pognan s klicem funkcije `main(port(int))`. Pri programiranju bodite pozorni, da bo strežnik poslušal na številki vrat, ki jih dobite v spremenljivki `port`, in ne le kakšni vnaprej zakodirani številki (npr. `8080`).

Vsa vprašanje v zvezi z nalogo zastavite v [forum](https://ucilnica.fri.uni-lj.si/mod/forum/view.php?id=9432) ali vprašajte na vajah oz. govorilnih urah.
