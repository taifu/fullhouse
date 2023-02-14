#!/usr/bin/env python
# -*- coding: Latin-1 -*-

"""
Full House

Scritto da Marco Beri <mberi@linkgroup.it>
Basato su un'idea di Erich Friedman <efriedma@stetson.edu>

fullhouse_engine.py: motore del gioco
fullhouse_problemi.py: lista dei problemi da risolvere
fullhouse.py: interfaccia grafica

"""

# Caselle
CASELLA_BIANCA = 0
CASELLA_NERA = 1
CASELLA_OCCUPATA = 2

# Classe per gestire una direzione di movimento
class Direzione:
    def __init__(self, d_x, d_y):
        self.d_x = d_x
        self.d_y = d_y

    # Due Direzioni con uguali delta sono uguali
    def __eq__(self, direzione):
        return self.d_x == direzione.d_x and self.d_y == direzione.d_y

    # Ritorna la direzione opposta
    def Opposta(self):
        if self == NORD:
            return SUD
        elif self == SUD:
            return NORD
        elif self == EST:
            return OVEST
        elif self == OVEST:
            return EST
        raise Exception("direzione sconosciuta %d" % self)
    
    # Rappresentazione comprensibile della posizione
    def __repr__(self):
        if self == NORD:
            s = "NORD"
        elif self == SUD:
            s = "SUD"
        elif self == EST:
            s = "EST"
        elif self == OVEST:
            s = "OVEST"
        else:
            s = "(%d, %d)" % (self.d_x, self.d_y)
        return "<Direzione %s>" % s

# Direzioni cardinali
NORD = Direzione(0, -1)
EST = Direzione(1, 0)
SUD = Direzione(0, 1)
OVEST = Direzione(-1, 0)
DIREZIONI = (NORD, EST, SUD, OVEST)

# Classe per gestire una posizione sulla scacchiera
class Posizione:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Due posizioni con uguali coordinate sono uguali
    def __eq__(self, posizione):
        return self.x == posizione.x and self.y == posizione.y
    
    # Rappresentazione comprensibile della posizione
    def __repr__(self):
        return "<Posizione instance x=%d, y=%d>" % (self.x, self.y)
    
    # In base alla direzione ritorna la posizione contigua
    def Contigua(self, direzione):
        if not direzione in DIREZIONI:
            raise Exception("direzione sconosciuta %s" % direzione)
        return Posizione(self.x + direzione.d_x, self.y + direzione.d_y)

    # Controlla se la posizione passata e` in una delle
    # direzioni cardinali rispetto all'istanza self.
    # Se lo e`, ritorna la direzione.
    # Se non lo e`, ritorna None.
    def Direzione(self, posizione):
        # Per essere nella stessa direzione una delle
        # due coordinate deve essere la stessa
        if posizione.x == self.x:
            if posizione.y > self.y:
                return SUD
            elif posizione.y < self.y:
                return NORD
        elif posizione.y == self.y:
            if posizione.x > self.x:
                return EST
            elif posizione.x < self.x:
                return OVEST
        return None   

# Classe per gestire la scacchiera di gioco
class Scacchiera:
    def __init__(self, dimensione, posizioni_nere = ()):
        self.dimensione = dimensione
        self.posizioni_nere = list(posizioni_nere)
        self.Reset()

    # Crea la scacchiera e azzera le mosse
    def Reset(self):
        self.posizioni = []
        self.direzioni = []
        self.matrice = []
        for x in range(self.dimensione):
            self.matrice.append([ CASELLA_BIANCA ] * self.dimensione)
        for posizione in self.posizioni_nere:
            self.matrice[posizione.x][posizione.y] = CASELLA_NERA

    # Rappresentazione comprensibile della Scacchiera
    def __repr__(self):
        s = " %s\n" % ("-" * self.dimensione)
        for y in range(self.dimensione):
            s += "|"
            for x in range(self.dimensione):
                if self.matrice[x][y] == CASELLA_BIANCA:
                    s += " "
                elif self.matrice[x][y] == CASELLA_NERA:
                    s += "X"
                elif self.matrice[x][y] == CASELLA_OCCUPATA:
                    s += "."
                else:
                    s += "E"
                    s += "X"
            s += "|\n"
        s += " %s\n" % ("-" * self.dimensione)
        return "<Scacchiera dimensione=%d>\n%s" % (self.dimensione, s)
    
    # Controlla se una posizione e` percorribile, quindi
    # se e` interna alla matrice e se non e` gia` occupata o nera
    def Percorribile(self, posizione):
        if posizione.x < 0 or posizione.x >= self.dimensione or \
               posizione.y < 0 or posizione.y >= self.dimensione or \
               not self.matrice[posizione.x][posizione.y] == CASELLA_BIANCA:
            return False
        return True

    # Occupa la casella della posizione passata
    def Occupa(self, posizione):
        self.matrice[posizione.x][posizione.y] = CASELLA_OCCUPATA

    # Libera la casella della posizione passata
    def Libera(self, posizione):
        self.matrice[posizione.x][posizione.y] = CASELLA_BIANCA

    # Controlla se la matrice e` completa e quindi risolta
    def Risolta(self):
        for x in range(self.dimensione):
            for y in range(self.dimensione):
                if self.Percorribile(Posizione(x, y)):
                    return False
        return True
        
    # Controlla se si e` un punto morto
    def PuntoMorto(self):
        for direzione in DIREZIONI:
            if self.Percorribile(self.posizioni[-1].Contigua(direzione)):
                return False
        return True
        
    # Muovi dalla posizione corrente nella direzione scelta.
    # Se percorribile ritorna il numero di caselle percorse,
    # altrimenti ritorna 0
    def Percorri(self, direzione):
        caselle_percorse = 0
        posizione_corrente = self.posizioni[-1]
        while True:
            posizione_seguente = posizione_corrente.Contigua(direzione)
            if not self.Percorribile(posizione_seguente):
                # Se ho percorso almeno una casella
                # salvo la direzione e la posizione attuale
                if caselle_percorse > 0:
                    self.direzioni.append(direzione)
                    self.posizioni.append(posizione_corrente)
                return caselle_percorse
            caselle_percorse += 1
            posizione_corrente = posizione_seguente
            self.Occupa(posizione_corrente)

    # "Clicca" una casella. Se possibile, questo causa
    # il movimento nella direzione prescelta dalla casella.
    # Se e` la prima mossa, setta solo la posizione iniziale.
    # Se e` successiva setta anche la direzione scelta.
    # Se la mossa e` accettabile ritorna True, altrimenti False
    def Click(self, posizione):
        # Innanzitutto la casella deve essere libera
        if self.Percorribile(posizione):
            # Se e` la prima mossa, la salva
            if len(self.posizioni) == 0:
                self.Occupa(posizione)
                self.posizioni.append(posizione)
                return True
            # Controlla che la casella cliccata indichi
            # una direzione accettabile
            direzione = self.posizioni[-1].Direzione(posizione)
            if direzione and self.Percorri(direzione) > 0:
                return True
        return False

    # Annulla l'ultima mossa fatta
    def Annulla(self):
        if len(self.direzioni) > 0:
            direzione = self.direzioni.pop().Opposta()
            posizione_corrente = self.posizioni.pop()
            while True:
                self.Libera(posizione_corrente)
                posizione_seguente = posizione_corrente.Contigua(direzione)
                if posizione_seguente == self.posizioni[-1]:
                    break
                posizione_corrente = posizione_seguente
            return True
        elif len(self.posizioni) > 0:
            self.Libera(self.posizioni.pop())
            return True
        return False

    # Esplora ricorsivamente la matrice a partire dalla posizione corrente
    def Esplora(self):
        if self.Risolta():
            self.soluzioni.append((self.posizioni[0],) + tuple(self.direzioni[:]))
            return
        for direzione in DIREZIONI:
            if self.Click(self.posizioni[-1].Contigua(direzione)):
                self.Esplora()
                self.Annulla()

    # Risolve il problema
    def Risolvi(self):
        self.Reset()
        self.soluzioni = []
        for x in range(self.dimensione):
            for y in range(self.dimensione):
                #self.posizioni = [Posizione(x, y)]
                #if self.percorribile(self.posizioni[0]):
                #    #self.occupa(self.posizioni[0])
                #    self.muovi(self.posizioni[0])
                if self.Click(Posizione(x, y)):
                    self.Esplora()
                    self.Annulla()
        return self.soluzioni

# Funzione di test
def Test():
    # Gioco di esempio con relativa soluzione
    dimensione = 5
    posizioni_nere = (Posizione(0, 2), Posizione(3, 3), Posizione(4, 1))
    soluzione = (Posizione(4, 0),
                 OVEST, SUD, EST, SUD, EST, SUD,
                 OVEST, NORD, EST, NORD, OVEST)

    #dimensione = 9
    #posizioni_nere = (Posizione(1,1), Posizione(1,2), Posizione(4,4),
    #                  Posizione(6,2), Posizione(7,4), Posizione(7,5))
    #soluzione = (Posizione(5, 2),
    #             OVEST, NORD, OVEST, SUD, EST,
    #             NORD, OVEST, SUD, EST, SUD,
    #             OVEST, SUD, EST, NORD, OVEST,
    #             NORD, EST, SUD, EST, NORD, OVEST)
    
    # Crea la scacchiera del problema di test
    s = Scacchiera(dimensione = dimensione, posizioni_nere = posizioni_nere)

    # Verifica che le caselle nere corrispondano
    for x in range(dimensione):
        assert len(s.matrice[x]) == dimensione
        for y in range(dimensione):
            if Posizione(x, y) in posizioni_nere:
                assert s.matrice[x][y] == CASELLA_NERA
            else:
                assert s.matrice[x][y] == CASELLA_BIANCA

    # Verifica che la risoluzione contempi una
    # sola soluzione identica a quella nota
    soluzioni = s.Risolvi()
    assert len(soluzioni) == 1
    assert soluzioni[0] == soluzione

# Se eseguito come script, effettua solo il test
if __name__ == "__main__":
    Test()
