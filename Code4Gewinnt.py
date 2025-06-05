'''
Dies ist ein Code für das Spielfeld von 4 Gewinnt, welches mit den Codes Client4Gewinnt und Server4Gewinnt per sockets spielbar ist.
Creators:
    Julia
    Matteo
Prüfstelle:
    HTL-Anichstrasse
'''

import tkinter as tk

# Konstanten für das Spielfeld
REIHEN = 6
SPALTEN = 7
ZELL_GROESSE = 60  # Pixelgröße der Zellen

# Farben für Spieler
FARBEN = {"X": "#f13914", "O": "#e6e51d", " ": "#f1f1f1"}
NAMEN = {"X": "Rot", "O": "Gelb"}

class VierGewinntGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("4 Gewinnt – Julia & Matteo")
        
        # Neustart-Button
        self.reset_button = tk.Button(root, text="Spiel Neustarten", command=self.spiel_neustarten)
        self.reset_button.grid(row=2, column=0, columnspan=SPALTEN, pady=10)

        # Spielfeld-Datenstruktur
        self.feld = [[" " for _ in range(SPALTEN)] for _ in range(REIHEN)]

        # Spieler starten mit "X"
        self.spieler = "X"
        self.spiel_aktiv = True

        # Canvas erstellen
        self.canvas = tk.Canvas(root, width=SPALTEN * ZELL_GROESSE, height=REIHEN * ZELL_GROESSE, bg="#1207c1")
        self.canvas.grid(row=0, column=0, columnspan=SPALTEN)

        # Buttons zum Steine setzen
        self.buttons = []
        for spalte in range(SPALTEN):
            btn = tk.Button(root, text=str(spalte + 1), width=4, command=lambda s=spalte: self.chip_setzen(s))
            btn.grid(row=1, column=spalte, padx=2, pady=4)
            self.buttons.append(btn)

        self.zeichne_feld()

    def zeige_status_text(self, text, farbe="black"):
        # Vorherige Textanzeige löschen
        if self.status_text_id:
            self.canvas.delete(self.status_text_id)

        # Position des Textes berechnen (zentriert im Spielfeld)
        x = (SPALTEN * ZELL_GROESSE) // 2
        y = (REIHEN * ZELL_GROESSE) // 2

        # Hintergrundbox erstellen (weißer Hintergrund mit schwarzem Rand)
        box = self.canvas.create_rectangle(
            x - 160, y - 40, x + 160, y + 40,  # Rechteck Position
            fill="white", outline="black", width=3  # Hintergrundfarbe und Rand
        )

        # Text im Zentrum des Rechtecks mit der gewünschten Farbe und Schriftart
        self.status_text_id = self.canvas.create_text(
            x, y, text=text, fill=farbe, font=("Arial", 24, "bold")
        )


    def zeichne_feld(self):
        self.canvas.delete("all")
        for zeile in range(REIHEN):
            for spalte in range(SPALTEN):
                x1 = spalte * ZELL_GROESSE + 5
                y1 = zeile * ZELL_GROESSE + 5
                x2 = x1 + ZELL_GROESSE - 10
                y2 = y1 + ZELL_GROESSE - 10
                farbe = FARBEN[self.feld[zeile][spalte]]
                self.canvas.create_oval(x1, y1, x2, y2, fill=farbe, outline="black")

    def spiel_neustarten(self):
        self.feld = [[" " for _ in range(SPALTEN)] for _ in range(REIHEN)]
        self.spieler = "X"
        self.spiel_aktiv = True
        self.zeichne_feld()


    def chip_setzen(self, spalte):
        if not self.spiel_aktiv:
            return

        gesetzt = False  # Flag für erfolgreichen Zug
        for zeile in reversed(range(REIHEN)):
            if self.feld[zeile][spalte] == " ":
                self.feld[zeile][spalte] = self.spieler
                self.zeichne_feld()
                gesetzt = True
                if self.pruefe_gewinner(zeile, spalte):
                    self.canvas.create_text(
                        (SPALTEN * ZELL_GROESSE) // 2,
                        (REIHEN * ZELL_GROESSE) // 2,
                        text=f"Spieler {NAMEN[self.spieler]}\n gewinnt!",
                        font=("Arial", 32, "bold"), fill="green"
                    )
                    self.spiel_aktiv = False
                    return
                elif self.spielfeld_voll():
                    self.canvas.create_text(
                        (SPALTEN * ZELL_GROESSE) // 2,
                        (REIHEN * ZELL_GROESSE) // 2,
                        text="Unentschieden!",
                        font=("Arial", 24), fill="white"
                    )
                    self.spiel_aktiv = False
                    return
                else:
                    # Nur wechseln, wenn ein Chip gesetzt wurde
                    self.spieler = "O" if self.spieler == "X" else "X"
                return

        print("Spalte voll!")  # Fehleranzeige für volle Spalte

    def spielfeld_voll(self):
        return all(self.feld[0][spalte] != " " for spalte in range(SPALTEN))

    def pruefe_gewinner(self, zeile, spalte):
        def zaehle_richtung(dz, ds):
            count = 0
            z, s = zeile + dz, spalte + ds
            while 0 <= z < REIHEN and 0 <= s < SPALTEN and self.feld[z][s] == self.spieler:
                count += 1
                z += dz
                s += ds
            return count

        richtungen = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dz, ds in richtungen:
            count = 1 + zaehle_richtung(dz, ds) + zaehle_richtung(-dz, -ds)
            if count >= 4:
                return True
        return False

