# Reseptit

## Ominaisuudet
- Sovelluksessa käyttäjät pystyvät jakamaan ruokareseptejään. Reseptissä lukee tarvittavat ainekset ja valmistusohje.
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään reseptejä, muokkaamaan ja poistamaan niitä.
- Käyttäjä näkee sovellukseen lisätyt reseptit.
- Käyttäjä pystyy etsimään reseptejä hakusanalla.
- Käyttäjä pystyy antamaan reseptille arvostelun, jossa on kommentti ja arvosana.
- Reseptistä näytetään arvostelut.
- Käyttäjäsivu näyttää, listan käyttäjän lisäämistä resepteistä ja montako reseptiä ja arvostelua käyttäjä on lisännyt.

### Tulossa
- Reseptistä näytetään keskimääräinen arvosana.
- Käyttäjä pystyy valitsemaan reseptille yhden tai useamman luokittelun (esim. alkuruoka, intialainen, vegaaninen).
- Käyttäjä pystyy lisäämään reseptille kuvan.
- Ulkonäkö/käytettävyys muutoksia:
  - Fontit suuremmiksi monessa kohtaa.
  - Eri sivuille omat otsikot.
  - Painikkeet selkeämmiksi. (Erottelua tärkeyden mukaan, luettavammat värit/fontit)
  - Käyttäjälle parempi palaute arvostelun lähetyksestä.


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
