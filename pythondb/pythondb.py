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
            ## ce ni podatka o starosti
            if line[6] == '':
                line[6] = None
            cur.execute("""
                INSERT INTO igra
                (ime, min_igralcev, max_igralcev, min_cas, max_cas, leto_izdaje, starost)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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