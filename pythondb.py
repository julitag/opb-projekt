#!/usr/bin/python
# -*- encoding: utf-8 -*-

import auth
import psycopg2, psycopg2.extensions, psycopg2.extras
import csv
import re

## vpisi ukaze za ustvarjanje/brisanje tabel, dodajanje podatkov

###################

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) ## šumniki
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password) ## povezava z bazo
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) ## izvede se autocommit
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) ## na kurzorju izvedem ukaz in dobim rezultat, vedno po en pa po en

###################

## from pythondb import *
## vpisi ustvari_igra() v shell, da se ustvari tabela v bazi
## ce si se zmotil: conn.rollback()

def ustvari_igra():
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

def pobrisi_igra():
    cur.execute("""
        DROP TABLE igra;
    """)
    conn.commit()

def uvozi_igra():
    with open("tabele/igre.csv", encoding='utf-8') as f:
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
            tip TEXT NOT NULL CHECK (tip in ('gost', 'registriranec', 'moderator')),
            username TEXT NOT NULL,
            mail TEXT NOT NULL,
            geslo TEXT NOT NULL
        )
    """)
    cur.execute("""
        SELECT SETVAL(pg_get_serial_sequence('uporabnik', 'id'), 1000)
    """)
    conn.commit()

def pobrisi_uporabnik():
    cur.execute("""
        DROP TABLE uporabnik
    """)
    conn.commit()

def dodaj_pravice():
    cur.execute("""
        GRANT CONNECT ON DATABASE sem2019_gasperl TO javnost
    """)
    ## grant usage daje dostop do tabel. izjemoma za public ni potrebno, ker imajo po defaultu uporabniki CREATE and USAGE privilegije na PUBLIC shema
    ## brez grant ostali dostopi nimajo smisla
    ## schema je zbirka podatkovnih objektov, ki je asociirana z neko doloceno bazo
    cur.execute("""
        GRANT USAGE ON SCHEMA public TO javnost
    """)
    cur.execute("""
        GRANT SELECT, UPDATE, INSERT ON ALL TABLES IN SCHEMA public TO javnost
    """)
    ## sequences za generiranje stevilk, vrednosti za kljuce, itd...
    cur.execute("""
        GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO javnost;
    """)
    conn.commit()
