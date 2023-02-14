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

import wx
from wx.lib.wordwrap import wordwrap
from fullhouse_engine import Scacchiera, Posizione, Direzione
from fullhouse_problemi import Problemi

# Classe che si occupa di disegnare la
# finestra della schacchiera
class FullHouseWindow(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent,
                           id = -1,
                           pos = wx.Point(0, 0),
                           size = wx.DefaultSize,
                           style = wx.SUNKEN_BORDER | wx.WANTS_CHARS |
                           wx.FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour(wx.NamedColour("white"))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftClick)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
        self.scacchiera = Problemi[0]
        self.edit_mode = False

    # Calcola l'area di un riquadro di una posizione
    # tornando il corrispondente wx.Rect
    def CalcolaRiquadro(self, posizione):
        return wx.Rect(self.alto_sinistra.x + self.lato_casella * posizione.x,
                       self.alto_sinistra.y + self.lato_casella * posizione.y,
                       self.lato_casella, self.lato_casella)

    # Controlla se un punto e` interno ad un riquadro
    # e ne ritorna le coordinate altrimenti ritorna (None, None) 
    def ControllaPunto(self, punto):
        for x in range(self.scacchiera.dimensione):
            for y in range(self.scacchiera.dimensione):
                riquadro = self.CalcolaRiquadro(Posizione(x, y))
                riquadro.Deflate(self.bordo, self.bordo)
                if riquadro.Contains(punto):
                    return (x, y)
        return (None, None)

    # Disegna il contenuto della finestra
    def OnPaint(self, event):
        # Calcola la dimensione della finestra
        x, y = self.GetSize()

        # Calcola la posizione e la dimensione della
        # scacchiera quadrata e la dimensione dei riquadri
        self.lato_casella =  int(min(x, y) * 0.8 / self.scacchiera.dimensione)
        self.lato_scacchiera =  self.lato_casella * self.scacchiera.dimensione
        self.alto_sinistra = wx.Point((x - self.lato_scacchiera)/2, (y - self.lato_scacchiera)/2 * 1.2)
        self.bordo = self.lato_casella / 15
        self.mezzo_riquadro = wx.Point(self.lato_casella / 2, self.lato_casella / 2)
        self.raggio = self.lato_casella / 2 - self.bordo

        # Istanzia l'oggetto per il disegno
        w, h = self.GetClientSizeTuple()
        buffer = wx.EmptyBitmap(w, h)
        dc = wx.PaintDC(self)
  
        # Scrive la modalita` corrente
        if self.edit_mode:
            font = dc.GetFont()
            font.SetPointSize(20)
            dc.SetFont(font)
            msg_edit = "EDIT"
            w, h = dc.GetTextExtent(msg_edit)
            dc.DrawText(msg_edit, (x - w)/2, (self.alto_sinistra.y - h)/2)

        # Disegna la scacchiera
        dc.SetPen(wx.Pen(wx.NamedColour("black"), 1, wx.SOLID))
        dc.SetBrush(wx.Brush(wx.NamedColour("grey")))

        # Disegna le righe della scacchiera
        punto = wx.Point(self.alto_sinistra.x, self.alto_sinistra.y)
        for colonne in range(self.scacchiera.dimensione + 1):
            dc.DrawLines([punto, punto + wx.Point(0, self.lato_scacchiera)])
            punto += wx.Point(self.lato_casella, 0)
            
        # Disegna le colonne della scacchiera
        punto = wx.Point(self.alto_sinistra.x, self.alto_sinistra.y)
        for righe in range(self.scacchiera.dimensione + 1):
            dc.DrawLines([punto, punto + wx.Point(self.lato_scacchiera, 0)])
            punto += wx.Point(0, self.lato_casella)
            
        # Disegna le caselle nere della scacchiera
        for posizione_nera in self.scacchiera.posizioni_nere:
            riquadro_nero = self.CalcolaRiquadro(posizione_nera)
            riquadro_nero.Deflate(self.bordo, self.bordo)
            dc.DrawRectangle(riquadro_nero.x, riquadro_nero.y,
                             riquadro_nero.width, riquadro_nero.height)

        # Disegna le mosse
        if len(self.scacchiera.posizioni) > 0:
            dc.SetPen(wx.Pen(wx.NamedColour("red"), self.lato_casella / 5, wx.SOLID))
            for cont, direzione in enumerate(self.scacchiera.direzioni):
                posizione_da = self.scacchiera.posizioni[cont]
                posizione_finale = self.scacchiera.posizioni[cont + 1]
                while True:
                    posizione_a = posizione_da.Contigua(direzione)
                    punto_da = self.CalcolaRiquadro(posizione_da).GetTopLeft() + self.mezzo_riquadro
                    punto_a = self.CalcolaRiquadro(posizione_a).GetTopLeft() + self.mezzo_riquadro
                    dc.DrawLines([punto_da, punto_a])
                    posizione_da = posizione_a
                    if posizione_a == posizione_finale:
                        break
            # Disegna la mossa iniziale
            dc.SetPen(wx.Pen(wx.NamedColour("orange"), 1, wx.SOLID))
            dc.SetBrush(wx.Brush(wx.NamedColour("orange")))
            centro = self.CalcolaRiquadro(self.scacchiera.posizioni[0]).GetTopLeft() + self.mezzo_riquadro
            dc.DrawCircle(centro.x, centro.y, self.raggio)

    # Annulla l'ultima mossa
    def Annulla(self):
        if self.scacchiera.Annulla():
            self.Refresh()

    # Azzera il problema
    def Azzera(self):
        # Flag vari
        self.aiuto = False
        self.scacchiera.Reset()
        self.Refresh()

    # Modalita` di creazione di un nuovo problema
    def EditOnOff(self, set_edit = None):
        if set_edit == None:
            self.edit_mode = not self.edit_mode
        else:
            self.edit_mode = set_edit
        self.menu_edit_item.Check(self.edit_mode)
        self.scacchiera.Reset()
        self.Refresh()

    # Sceglie il problema corrente
    def Problema(self, scacchiera):
        self.scacchiera = scacchiera
        self.Azzera()

    # Risolve da solo il problema
    def Risolve(self):
        self.Azzera()
        self.aiuto = True
        soluzioni = self.scacchiera.Risolvi()
        if len(soluzioni) > 0:
            if len(soluzioni) > 1:
                self.Messaggio("Ci sono %d soluzioni!" % len(soluzioni), "Risolvi",
                             wx.OK | wx.ICON_EXCLAMATION)
            self.edit_mode = False
            self.Click(soluzioni[0][0])
            self.Update()
            wx.MilliSleep(250)
            for direzione in soluzioni[0][1:]:
                self.Click(self.scacchiera.posizioni[-1].Contigua(direzione))
                self.Update()
                wx.MilliSleep(250)
            self.edit_mode = self.menu_edit_item.IsChecked()
            self.Refresh()
        else:
            self.Messaggio("Nessuna soluzione!", "Risolvi",
                         wx.OK | wx.ICON_EXCLAMATION)

    # Gestisce il click destro del mouse
    # che annulla l'ultima mossa
    def OnRightClick(self, event):
        self.Annulla()

    # Gestisce il click destro del mouse
    # che effettua una nuova mossa
    def OnLeftClick(self, event):
        point_click = wx.Point(event.m_x, event.m_y)
        x, y = self.ControllaPunto(point_click)
        if x != None:
            self.Click(Posizione(x, y))
       
    # Visualizza un messaggio
    def Messaggio(self, testo, titolo, stile):
        dlg = wx.MessageDialog(self, testo, titolo, stile)
        dlg.ShowModal()
        dlg.Destroy()
    
    # Effettua una nuova mossa oppure, se
    # in edit_mode, cambia lo stato di una casella
    def Click(self, posizione):
        if self.edit_mode:
            if posizione in self.scacchiera.posizioni_nere:
                self.scacchiera.posizioni_nere.remove(posizione)
            else:
                self.scacchiera.posizioni_nere.append(posizione)
            self.scacchiera.Reset()
            self.Refresh()
        elif self.scacchiera.Click(posizione):
            self.Refresh()
            # Verifica la risoluzione del problema
            if self.scacchiera.Risolta():
                # Se e` stato scelto l'aiuto
                if self.aiuto:
                    msg = self.Messaggio("Troppo facile con l'aiuto...", "Fine",
                                         wx.OK | wx.ICON_EXCLAMATION)
                else:
                    msg = self.Messaggio("Hai risolto questo problema!", "Fine",
                                         wx.OK | wx.ICON_EXCLAMATION)
            # Verifica l'arrivo ad un punto morto
            elif self.scacchiera.PuntoMorto():
                msg = self.Messaggio("Sei ad un punto morto!", "Fine",
                                     wx.OK | wx.ICON_EXCLAMATION)

# Classe frame che gestisce il menu` e
# contiene la finestra della scacchiera
class FullHouseFrame(wx.Frame):
    def __init__(self, title):
        x, y = wx.ScreenDC().GetSize()
        size = (x/3, x/3)
        pos = (x/3, y/3)
        wx.Frame.__init__(self, parent=None, id=-1, title=title, size=size, pos=pos)
        self.fullHouseWindow = FullHouseWindow(self)
        self.CenterOnScreen()
        self.CreateStatusBar()

        # Menu` principale
        menuBar = wx.MenuBar()
        menu_principale = wx.Menu()
        menu_principale.Append(101, "&Esci", "Chiude il programma")
        menuBar.Append(menu_principale, "&File")

        # Menu` mosse
        menu_mosse = wx.Menu()
        menu_mosse.Append(201, "&Annulla mossa\tCtrl+A", "Annulla l'ultima mossa")
        menu_mosse.Append(202, "A&zzera partita\tCtrl+Z", "Riparte dall'inizio del problema")
        menu_mosse.AppendSeparator()
        menu_mosse.Append(203, "&Risolve partita\tCtrl+R", "Risolve il problema")
        menu_mosse.AppendSeparator()
        self.fullHouseWindow.menu_edit_item = menu_mosse.Append(204, "Modalità &edit\tCtrl+E",
                                                                "Inserisci un nuovo problema",
                                                                wx.ITEM_CHECK)
        menuBar.Append(menu_mosse, "&Edit")

        # Menu` problemi
        self.menu_problemi = wx.Menu()
        self.menu_problemi.Append(301, "&Seguente\tCtrl+S", "Passa al problema seguente")
        self.menu_problemi.Append(302, "&Precedente\tCtrl+P", "Torna al problema precedente")
        self.menu_problemi.AppendSeparator()
        self.problema_corrente = 0
        for cont, problema in enumerate(Problemi):
            self.menu_problemi.Append(303 + cont, "Problema %d (%d x %d)" %
                         (cont + 1, problema.dimensione, problema.dimensione),
                         "", wx.ITEM_RADIO )
        menuBar.Append(self.menu_problemi, "&Problemi")

        # Menu` help
        menu_help = wx.Menu()
        menu_help.Append(401, "&About", "Informazioni sul programma")
        menuBar.Append(menu_help, "&Help")

        self.SetMenuBar(menuBar)

        # Eventi Menu`
        self.Bind(wx.EVT_MENU, self.Esci, id=101)
        self.Bind(wx.EVT_MENU, self.Annulla, id=201)
        self.Bind(wx.EVT_MENU, self.Azzera, id=202)
        self.Bind(wx.EVT_MENU, self.Risolve, id=203)
        self.Bind(wx.EVT_MENU, self.Edit, id=204)
        self.Bind(wx.EVT_MENU, self.ProblemaSeguente, id=301)
        self.Bind(wx.EVT_MENU, self.ProblemaPrecedente, id=302)
        self.Bind(wx.EVT_MENU, self.Problema, id=303, id2=302 + len(Problemi))
        self.Bind(wx.EVT_MENU, self.About, id=401)

    def Esci(self, event):
        self.Close()

    def Azzera(self, event):
        self.fullHouseWindow.Azzera()

    def Edit(self, event):
        self.fullHouseWindow.EditOnOff()

    def Annulla(self, event):
        self.fullHouseWindow.Annulla()
        
    def Risolve(self, event):
        if self.fullHouseWindow.edit_mode:
            result = wx.ID_OK
        else:
            dialog = wx.MessageDialog(self,
                                      "Sei sicuro di rinunciare a farcela da solo?" ,
                                      "Risolve", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            result = dialog.ShowModal()
            dialog.Destroy()
        if result == wx.ID_OK:
            self.fullHouseWindow.Risolve()
        
    def Problema(self, event):
        self.problema_corrente = event.GetId() - 303
        self.fullHouseWindow.Problema(Problemi[self.problema_corrente])
        
    def ProblemaPrecedente(self, event):
        if self.problema_corrente > 0:
            self.problema_corrente -= 1
            self.menu_problemi.GetMenuItems()[self.problema_corrente + 3].Check(True)
            self.fullHouseWindow.Problema(Problemi[self.problema_corrente])
        
    def ProblemaSeguente(self, event):
        if self.problema_corrente + 1 < len(Problemi):
            self.problema_corrente += 1
            self.menu_problemi.GetMenuItems()[self.problema_corrente + 3].Check(True)
            self.fullHouseWindow.Problema(Problemi[self.problema_corrente])
        
    def About(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "Full House"
        info.Version = "1.0"
        info.Copyright = "(C) 2007 Marco Beri"
        info.Description = wordwrap(
            "\n\n" +
            "Scritto per il libro \"Pocket Python\" edito da Apogeo." +
            "\n\n" +
            "Basato su un idea di Erich Friedman.",
            350, wx.ClientDC(self))
        info.WebSite = ("mailto:mberi@linkgroup.it", "Marco Beri")
        info.Developers = [ "Marco Beri" ]

        # info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

class FullHouse(wx.App):
    def OnInit(self):
        fullhouse = FullHouseFrame("Full House")
        fullhouse.Show(True)
        self.SetTopWindow(fullhouse)
        return True

def main():
    fh = FullHouse(0)
    fh.MainLoop()

if __name__ == "__main__":
    main()
