#!/usr/bin/python
# -*- encoding: utf-8 -*-

import bottle
import auth as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import hashlib

bottle.debug(True)
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"

######################################################################
# Pomožne funkcije

def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

# Funkcija, ki v cookie spravi sporocilo
def set_sporocilo(tip, vsebina):
    bottle.response.set_cookie('message', (tip, vsebina), path='/', secret=secret)

# Funkcija, ki iz cookija dobi sporočilo, če je
def get_sporocilo():
    sporocilo = bottle.request.get_cookie('message', default=None, secret=secret)
    bottle.response.delete_cookie('message')
    return sporocilo

########################################################################

@bottle.route('/static/<filepath:path>') ## lokacija nasega filea, tip: path
def server_static(filepath): ## serviramo datoteko iz mape static
    return bottle.static_file(filepath, root='static')

@bottle.get('/login/') ## lokacija nasega filea, tip: path
def login_get(): ## serviramo datoteko iz mape static
    """Serviraj formo za login."""
    return bottle.template('login.html', napaka=None, username=None) ## na zacetku ni usernamea in napake

@bottle.post("/login/")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = bottle.request.forms.user
    # Izračunamo MD5 hash geslo, ki ga bomo spravili
    password = password_md5(bottle.request.forms.psw)
    # Preverimo, ali se je uporabnik pravilno prijavil
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT 1 FROM uporabnik WHERE username=%s AND geslo=%s",
              [username, password])
    if c.fetchone() is None:
        # Username in geslo se ne ujemata
        return bottle.template("login.html",
                               napaka="Nepravilna prijava", ## v template login nastavljeno opozorilo
                               username=username) ## ohranimo isto uporabnisko ime
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        bottle.response.set_cookie('username', username, path='/', secret=secret)
        bottle.redirect("/")

@bottle.get("/register/")
def register_get():
    """Prikaži formo za registracijo."""
    return bottle.template("register.html", 
                           username=None,
                           mail=None,
                           napaka=None)

@bottle.post("/register/")
def register_post():
    """Registriraj novega uporabnika."""
    username = bottle.request.forms.user
    mail = bottle.request.forms.mail
    password1 = bottle.request.forms.psw1
    password2 = bottle.request.forms.psw2
    # Ali uporabnik že obstaja?
    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("SELECT 1 FROM uporabnik WHERE username=%s", [username])
    if c.fetchone():
        # Uporabnik že obstaja
        return bottle.template("register.html",
                               username=username, ## ohranimo uporabnisko ime in mail, le geslo je potrebno se enkrat vpisati
                               mail=mail,
                               napaka='To uporabniško ime je že zavzeto')
    elif not password1 == password2:
        # Geslo se ne ujemata
        return bottle.template("register.html",
                               username=username,
                               mail=mail,
                               napaka='Gesli se ne ujemata')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        password = password_md5(password1)
        print("uspeh")
        c.execute("INSERT INTO uporabnik (username, mail, geslo) VALUES (%s, %s, %s)",
                  (username, mail, password))
        conn.commit()
        # Daj uporabniku cookie
        bottle.response.set_cookie('username', username, path='/', secret=secret)
        bottle.redirect("/")

####################################

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)

# poženemo strežnik na portu 8080, glej http://localhost:8080/
bottle.run(host='localhost', port=8080, reloader=True, debug=True)