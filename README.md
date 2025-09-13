# Reseptit


- Sovelluksessa käyttäjät pystyvät jakamaan ruokareseptejään. Reseptissä lukee tarvittavat ainekset ja valmistusohje.
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään reseptejä, muokkaamaan ja poistamaan niitä.
- Käyttäjä näkee sovellukseen lisätyt reseptit.
- Käyttäjä pystyy etsimään reseptejä hakusanalla.
- Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä.
- Käyttäjä pystyy valitsemaan reseptille yhden tai useamman luokittelun (esim. alkuruoka, intialainen, vegaaninen).
- Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.


Testaus:
- Kun olet kloonannut tiedostot koneellesi, tarvitset uuden tiedoston /reseptit/database.db
- Seuraavaksi on tarkoitus saada schema.sql-tiedostossa olevat taulut tietokantaan:
    - Voit kopioida taulut ja syöttää ne database.db tiedostoon sqlite3:n avulla.
    - Voit myös käyttää komentoa:
        $ sqlite3 database.db < schema.sql
