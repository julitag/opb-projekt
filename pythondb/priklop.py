#!/usr/bin/python
# -*- encoding: utf-8 -*-

import bottle
import auth_public as auth
import psycopg2
import psycopg2.extensions
import psycopg2.extras
import hashlib
import pythondb as db

bottle.debug(True)
# to je za kodiranje cookiejev v brskalniku, da jih uporabnik ne more spreminjati in s tem povzrocati zmedo
# trenutni cookieji v chromeu: more tools -> developer tools -> application -> cookies
# vsakic ko gremo na naso spletno stran, server vrne cookie
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"

######################################################################
# Pomožne funkcije


def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


def get_user(auto_login=True):
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    # Dobimo username iz piškotka
    username = bottle.request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        c.execute("SELECT tip, username, mail FROM uporabnik WHERE username=%s",
                  [username])
        r = c.fetchone()
        conn.commit()
        # c.close()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return r
        else:
            bottle.redirect('/login/')
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    if auto_login:
        bottle.redirect('/login/')
    else:
        return None

########################################################################


@bottle.route('/static/<filepath:path>')  # lokacija nasega filea, tip: path
def server_static(filepath):  # serviramo datoteko iz mape static
    return bottle.static_file(filepath, root='static')


@bottle.route("/")
def main():
    """Glavna stran."""
    # Iz cookieja dobimo uporabnika (ali ga preusmerimo na login, če nima cookija)
    (tip, username, mail) = get_user()

    igre = db.select_igra()
    # Vrnemo predlogo za glavno stran
    return bottle.template("index.html", uporabnik=username, igre=igre)


@bottle.get('/login/')
def login_get():
    """Serviraj formo za login."""
    return bottle.template('login.html', napaka=None, username=None)  # na zacetku ni usernamea in napake


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
    conn.commit()
    if c.fetchone() is None:
        # Username in geslo se ne ujemata
        return bottle.template("login.html",
                               napaka="Nepravilna prijava",  # v template login nastavljeno opozorilo
                               username=username)  # ohranimo isto uporabnisko ime
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        bottle.response.set_cookie(
            'username', username, path='/', secret=secret)
        bottle.redirect("/")


@bottle.get("/logout/")
def logout():
    """Pobriši cookie in preusmeri na login."""
    bottle.response.delete_cookie('username', path='/', secret=secret)
    bottle.redirect('/login/')


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
    conn.commit()
    if c.fetchone():
        # Uporabnik že obstaja
        return bottle.template("register.html",
                               # ohranimo uporabnisko ime in mail, le geslo je potrebno se enkrat vpisati
                               username=username,
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
        c.execute("INSERT INTO uporabnik (tip, username, mail, geslo) VALUES (%s, %s, %s, %s)",
                  ('uporabnik', username, mail, password))
        conn.commit()
        # Daj uporabniku cookie
        bottle.response.set_cookie(
            'username', username, path='/', secret=secret)
        bottle.redirect("/")


@bottle.get("/igra/<ime>")
def igra_get(ime):
    (tip, username, mail) = get_user()
    igre = db.select_igra()
    return bottle.template("igra.html", uporabnik=username, igre=igre, igra=ime)


@bottle.get("/brskalnik/")
def brskalnik_get():
    """Prikaži brskalnik iger. """
    (tip, username, mail) = get_user()
    return bottle.template("brskalnik.html", uporabnik=username)


@bottle.post("/brskalnik/")
def brskalnik_post():
    (tip, username, mail) = get_user()
    # pretvorimo prazno vrednost pri html-ju, '', v prazno vrednost python, None
    def nula(s): return None if s is '' else s

    st_igralcev = nula(bottle.request.forms.st_igralcev)
    cas = nula(bottle.request.forms.cas)
    starost = nula(bottle.request.forms.starost)
    leto = nula(bottle.request.forms.leto)

    c = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    c.execute("""
        SELECT * FROM igra
        WHERE (%s IS NULL OR min_igralcev <= %s)
        AND (%s IS NULL OR max_igralcev >= %s)
        AND (%s IS NULL OR max_cas <= %s)
        AND (%s IS NULL OR starost <= %s)
        AND (%s IS NULL OR leto_izdaje = %s)
     """, [st_igralcev, st_igralcev, st_igralcev, st_igralcev, cas, cas, starost, starost, leto, leto])
    
    igre = c.fetchall()
    return bottle.template("index.html", uporabnik=username, igre=igre)

####################################


conn = psycopg2.connect(database=auth.db, host=auth.host,
                        user=auth.user, password=auth.password)
# se znebimo problemov s šumniki
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

# poženemo strežnik na portu 8080, glej http://localhost:8080/
bottle.run(host='localhost', port=8080, reloader=True, debug=True)
