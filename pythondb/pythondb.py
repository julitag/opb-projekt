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
            starost INT
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
            r = [line[0], int(re.search(r'\d+', line[3]).group())]
            cur.execute("""
                INSERT INTO igra
                (ime, starost)
                VALUES (%s, %s)
                RETURNING id
            """, r)
            ## fetchone() dobi naslednji rezultat poizvedbe, prva vrednost je ID
            rid, = cur.fetchone()
            print("Uvožena igra %s z ID-jem %d" % (r[0], rid)) ## %s string %d integer ... string formating
    conn.commit()