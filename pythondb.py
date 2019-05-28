#!/usr/bin/python
# -*- encoding: utf-8 -*-

import auth
import psycopg2, psycopg2.extensions, psycopg2.extras, psycopg2.sql
import csv
import re

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) ## šumniki
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password) ## povezava z bazo
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) ## izvede se autocommit
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) ## na kurzorju izvedem ukaz in dobim rezultat, vedno po en pa po en

## python enter
## from pythondb import *
## vpisi ustvari_igra() v shell, da se ustvari tabela v bazi
## ce si se zmotil: conn.rollback()



##############################################################

## tabele s pridobljenimi podatki



def pobrisi(tabela):
    cur.execute(
        psycopg2.sql.SQL("""
        DROP TABLE {}
    """).format(psycopg2.sql.Identifier(tabela)))
    conn.commit()

def ustvari_igra():
    cur.execute("""
        CREATE TABLE igra (
            serijska SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            min_igralcev INT,
            max_igralcev INT,
            min_cas INT,
            max_cas INT,
            leto_izdaje INT,
            starost INT
        );
    """)
    cur.execute("""
        ALTER TABLE igra
        ADD COLUMN dodatek INT REFERENCES igra(serijska)
    """)
    cur.execute("""
        SELECT SETVAL(pg_get_serial_sequence('igra', 'serijska'), 10000)
    """)
    conn.commit()

def uvozi_igra():
    with open("tabele/igre.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            ## ce ni podatkov
            if line[1] == '':
                line[1] = None
                line[2] = None
            elif line[2] == '':
                line[2] = None
            if line[3] == '':
                line[3] = None
                line[4] = None
            elif line[4] == '':
                line[4] = None
            if line[6] == '':
                line[6] = None
            # osnovna igra
            if line[7] == '':
                line[7] = None
                cur.execute("""
                    INSERT INTO igra
                    (ime, min_igralcev, max_igralcev, min_cas, max_cas, leto_izdaje, starost, dodatek)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING serijska
                """, line)
                ## fetchone() dobi naslednji rezultat poizvedbe, prva vrednost je ID
                lineid, = cur.fetchone()
                print("Uvožena igra %s z ID-jem %d" % (line[0], lineid)) ## %s string %d integer ... string formating
            else:
                cur.execute("""
                    INSERT INTO igra
                    (ime, min_igralcev, max_igralcev, min_cas, max_cas, leto_izdaje, starost, dodatek)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 
                    (SELECT serijska FROM igra WHERE ime=%s))
                    RETURNING serijska
                """, line)
                ## fetchone() dobi naslednji rezultat poizvedbe, prva vrednost je ID
                lineid, = cur.fetchone()
                print("Uvožena igra %s z ID-jem %d" % (line[0], lineid)) ## %s string %d integer ... string formating
    conn.commit()

def ustvari_zvrst():
    cur.execute("""
        CREATE TABLE zvrst (
            zvrst_id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL
        );
    """)
    cur.execute("""
        SELECT SETVAL(pg_get_serial_sequence('zvrst', 'zvrst_id'), 1000)
    """)
    conn.commit()

def uvozi_zvrst():
    with open("tabele/zvrsti.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            cur.execute("""
                INSERT INTO zvrst (ime)
                VALUES (%s)
            """, (line[0], ))
    conn.commit()

def ustvari_igrazvrst():
    cur.execute("""
        CREATE TABLE igrazvrst (
            serijska INT REFERENCES igra(serijska),
            zvrst_id INT REFERENCES zvrst(zvrst_id),
            PRIMARY KEY(serijska, zvrst_id)
        );
    """)
    conn.commit()

def uvozi_igrazvrst():
    with open("tabele/igrazvrst.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            try:
                cur.execute("""
                    INSERT INTO igrazvrst (serijska, zvrst_id)
                        SELECT serijska, zvrst_id FROM igra, zvrst WHERE igra.ime=%s AND zvrst.ime=%s
                """, line)
            ## nekatere igre imajo vec verzij in so zato imene podvojena v excelu, tako da ce se select stavek ponovi, javimo izjemo
            except psycopg2.errors.UniqueViolation as e:
                print("Igra %s je že vnesena" % line[0])
    conn.commit()

def ustvari_ustvarjalci():
    cur.execute("""
        CREATE TABLE ustvarjalci (
            u_id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            tip TEXT NOT NULL CHECK (tip in ('avtor', 'oblikovalec'))
        );
    """)
    cur.execute("""
        SELECT SETVAL(pg_get_serial_sequence('ustvarjalci', 'u_id'), 10000)
    """)
    conn.commit()

def uvozi_ustvarjalci():
    with open("tabele/avtor.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            cur.execute("""
                INSERT INTO ustvarjalci (ime, tip)
                VALUES (%s, 'avtor')
            """, (line[0], ))
    with open("tabele/oblikovalci.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            cur.execute("""
                INSERT INTO ustvarjalci (ime, tip)
                VALUES (%s, 'oblikovalec')
            """, (line[0], ))
    conn.commit()

def ustvari_igraust():
    cur.execute("""
        CREATE TABLE igraust (
            serijska INT REFERENCES igra(serijska),
            u_id INT REFERENCES ustvarjalci(u_id),
            PRIMARY KEY(serijska, u_id)
        );
    """)
    conn.commit()

def uvozi_igraust():
    with open("tabele/igraavtor.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            try:
                cur.execute("""
                    INSERT INTO igraust (serijska, u_id)
                        SELECT serijska, u_id FROM igra, ustvarjalci WHERE igra.ime=%s AND tip='avtor' AND ustvarjalci.ime=%s
                """, line)
            ## nekatere igre imajo vec verzij in so zato imene podvojena v excelu, tako da ce se select stavek ponovi, javimo izjemo
            except psycopg2.errors.UniqueViolation as e:
                print("Igra %s je že vnesena" % line[0])
    with open("tabele/igraoblikovalec.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            try:
                cur.execute("""
                    INSERT INTO igraust (serijska, u_id)
                        SELECT serijska, u_id FROM igra, ustvarjalci WHERE igra.ime=%s AND tip='oblikovalec' AND ustvarjalci.ime=%s
                """, line)
            ## nekatere igre imajo vec verzij in so zato imene podvojena v excelu, tako da ce se select stavek ponovi, javimo izjemo
            except psycopg2.errors.UniqueViolation as e:
                print("Igra %s je že vnesena" % line[0])
    conn.commit()

def ustvari_zalozba():
    cur.execute("""
        CREATE TABLE zalozba (
            zalozba_id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL
        );
    """)
    cur.execute("""
        SELECT SETVAL(pg_get_serial_sequence('zalozba', 'zalozba_id'), 10000)
    """)
    conn.commit()

def uvozi_zalozba():
    with open("tabele/zalozba.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            cur.execute("""
                INSERT INTO zalozba (ime)
                VALUES (%s)
            """, (line[0], ))
    conn.commit()

def ustvari_igrazal():
    cur.execute("""
        CREATE TABLE igrazal (
            serijska INT REFERENCES igra(serijska),
            zalozba_id INT REFERENCES zalozba(zalozba_id),
            PRIMARY KEY(serijska, zalozba_id)
        );
    """)
    conn.commit()

def uvozi_igrazal():
    with open("tabele/igrazalozba.csv", encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for line in rd:
            try:
                cur.execute("""
                    INSERT INTO igrazal (serijska, zalozba_id)
                        SELECT serijska, zalozba_id FROM igra, zalozba WHERE igra.ime=%s AND zalozba.ime=%s
                """, line)
            ## nekatere igre imajo vec verzij in so zato imene podvojena v excelu, tako da ce se select stavek ponovi, javimo izjemo
            except psycopg2.errors.UniqueViolation as e:
                print("Igra %s je že vnesena" % line[0])
    conn.commit()

###############################

## tabele uporabnikov, sporocil in ocen



def ustvari_uporabnik():
    cur.execute("""
        CREATE TABLE uporabnik (
            uporabnik_id SERIAL PRIMARY KEY,
            tip TEXT NOT NULL CHECK (tip in ('gost', 'registriranec', 'moderator')),
            username TEXT NOT NULL,
            mail TEXT NOT NULL,
            geslo TEXT NOT NULL
        )
    """)
    cur.execute("""
        SELECT SETVAL(pg_get_serial_sequence('uporabnik', 'uporabnik_id'), 10000)
    """)
    conn.commit()




###################################

## dodajanje pravic



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

def dodaj_pravice_julita():
    cur.execute("""
        GRANT CONNECT ON DATABASE sem2019_gasperl TO julitag
    """)
    cur.execute("""
        GRANT USAGE ON SCHEMA public TO julitag
    """)
    cur.execute("""
        GRANT ALL ON ALL TABLES IN SCHEMA public TO julitag
    """)
    cur.execute("""
        GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO julitag;
    """)
    conn.commit()