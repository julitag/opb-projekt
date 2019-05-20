import auth

import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import csv
import re

## povezava z bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)

## na kurzorju izvedem ukaz in dobim rezultat, vedno po en pa po en 
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def ustvari_tabelo_igra():
    cur.execute("""
        CREATE TABLE igra (
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            min_igralcev INT,
            max_igralcev INT,
            min_cas INT,
            max_cas INT,
            leto_izdaje INT,
            starost INT,
            tip char(1) -- spremenila
        );
    """)
    conn.commit()

## vpisi ustvari_tabelo() v IDLE, da se ustvari tabela na bazi
## ce si se zmotil: conn.rollback()

def pobrisi_tabelo_igra():
    cur.execute("""
        DROP TABLE igra;
    """)
    conn.commit()

def uvozi_podatke_igra():
    with open("pythondb/igre.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            ## ce ni podatka o starosti
            if line[6] == '':
                line[6] = None
            cur.execute("""
                INSERT INTO igra
                (ime, min_igralcev, max_igralcev, min_cas, max_cas, leto_izdaje, starost, tip)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, line)
            ## fetchone() dobi naslednji rezultat poizvedbe, prva vrednost je ID
            lineid, = cur.fetchone()
            print("Uvožena igra %s z ID-jem %d" % (line[0], lineid)) ## %s string %d integer ... string formating
    conn.commit()

def ustvari_uporabnik():
    cur.execute("""
        CREATE TABLE uporabnik (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            mail TEXT NOT NULL,
            geslo TEXT NOT NULL
        );
    """)
    conn.commit()

def pobrisi_uporabnik():
    cur.execute("""
        DROP TABLE uporabnik;
    """)
    conn.commit()


## ----------------------------------------------------------------vse spodi sem dodala------------------------------------------------------------------


def ustvari_tabelo_zanr():
    cur.execute("""
        CREATE TABLE zanr (
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL
        );
    """)
    conn.commit()

## vpisi ustvari_tabelo() v IDLE, da se ustvari tabela na bazi
## ce si se zmotil: conn.rollback()

def pobrisi_tabelo_zanr():
    cur.execute("""
        DROP TABLE zanr;
    """)
    conn.commit()

# za uvoz razlicnih podatkov, je treba najprej dobit vse podatke v eno 
# tabelo, nato pa izbrat distinct (ne mores it prek prehodne tabele, 
# ker imas tam foreign key

# ne vem a je bolj pametno it v vsaki vrstici ce se ni v tabeli, jo dodaj noter,
# al je bolj pametno nardit tabelo in potem vzet distinct? 
# je bolj pocasno pregledovanje podatkov al prepisovanje?


def uvozi_podatke_zanr():
    with open("pythondb/zvrst.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
		zanri = []
        for line in rd:
            ## v vrstici vzamemo vse elte
			vigri = line[1]
			vigri.split(",")
			zanri.extend(vigri)
		zanri(set(zanri))
        cur.execute("""
			INSERT INTO zanri (ime)
            VALUES (%s)
            RETURNING id
        """, zanri) ## ??? kako se tle nardi, da vstave vsako zanr v svojo vrstico?
		
		## vprasanje ----------------------------------------(gore)
		
		## fetchone() dobi naslednji rezultat poizvedbe, prva vrednost je ID
        lineid, = cur.fetchone()
        print("UvoÅ¾en Å¾anr %s z ID-jem %d" % (line[0], lineid))
conn.commit()


##  -----------------------tabela relacije igra-zanr

def ustvari_tabelo_relacija_zanr():
    cur.execute("""
        CREATE TABLE zanrRel (
            id SERIAL,
			igra TEXT FOREIGN KEY id REFERENCES igra,
			zanr TEXT FOREIGN KEY id REFERENCES zanr,
            PRIMARY KEY (igra, zanr)
        );
    """)
    conn.commit()

def pobrisi_tabelo_igra():
    cur.execute("""
        DROP TABLE zanrRel;
    """)
    conn.commit()

def uvozi_podatke_zanrRel():
    with open("pythondb/zvrst.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            ## ce ni podatka o zanru
            if line[1] == '':
                line[1] = None
			## vsak zanr dobi svojo vrstico
			vrstica = line[1]
			vrstica.split(",")
			for elt in vrstica
				cur.execute("""
					INSERT INTO zanrRel
					(igra, zanr)
					VALUES (%s, %s) -- to ne vem, kaj pomeni
					RETURNING id
				""", line)
            ## fetchone() dobi naslednji rezultat poizvedbe, prva vrednost je ID
            lineid, = cur.fetchone()
            print("UvoÅ¾ena igra %s z ID-jem %d" % (line[0], lineid)) ## %s string %d integer ... string formating
conn.commit()




