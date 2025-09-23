# Reseptit


- Sovelluksessa käyttäjät pystyvät jakamaan ruokareseptejään. Reseptissä lukee tarvittavat ainekset ja valmistusohje.
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään reseptejä, muokkaamaan ja poistamaan niitä.
- Käyttäjä näkee sovellukseen lisätyt reseptit.
- Käyttäjä pystyy etsimään reseptejä hakusanalla.
- Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä.
- Käyttäjä pystyy valitsemaan reseptille yhden tai useamman luokittelun (esim. alkuruoka, intialainen, vegaaninen).
- Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.


## Testaus
Asenna 'flask'-kirjasto:
```
$ pip install flask
```

Luo tiedosto 'reseptit/database.db'. Ja lisää sinne kuuluvat taulut:
```
$ sqlite3 database.db < schema.sql
```

Käynnistä sovellus:
```
$ flask run
```
