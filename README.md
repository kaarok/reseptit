# Reseptit

## Ominaisuudet
- Sovelluksessa käyttäjät pystyvät jakamaan ruokareseptejään. Reseptissä lukee tarvittavat ainekset ja valmistusohje.
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään reseptejä, muokkaamaan ja poistamaan niitä.
- Käyttäjä näkee sovellukseen lisätyt reseptit.
- Käyttäjä pystyy etsimään reseptejä hakusanalla.
- Käyttäjäsivu näyttää listan käyttäjän lisäämistä resepteistä.
- Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan.
- Reseptistä näytetään kommentit.

### Tulossa
- Reseptistä näytetään keskimääräinen arvosana.
- Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt.
- Käyttäjä pystyy valitsemaan reseptille yhden tai useamman luokittelun (esim. alkuruoka, intialainen, vegaaninen).
- Käyttäjä pystyy lisäämään reseptille kuvan.
- Ulkonäkö muutoksia:
  - Fontit suuremmiksi monessa kohtaa.
  - Eri sivuille omat otsikot.
  - Painikkeet selkeämmiksi.

## Testaus
Asenna 'flask'-kirjasto:
```
$ pip install flask
```

Luo tiedosto `reseptit/database.db`. Ja lisää sinne kuuluvat taulut:
```
$ sqlite3 database.db < schema.sql
```

Käynnistä sovellus:
```
$ flask run
```
