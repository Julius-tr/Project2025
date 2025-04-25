'''
Dies wird/ist ein 4 Gewinnt Multiplayer per sockets code
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

class VierGewinntGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("4 Gewinnt – Julia & Matteo")

        # Spielfeld-Datenstruktur
        self.feld = [[" " for _ in range(SPALTEN)] for _ in range(REIHEN)]

        # Spieler starten mit "X"
        self.spieler = "X"

        # Canvas erstellen
        self.canvas = tk.Canvas(root, width=SPALTEN * ZELL_GROESSE, height=REIHEN * ZELL_GROESSE, bg="#1207c1")
        self.canvas.grid(row=0, column=0, columnspan=SPALTEN)

        # Buttons zum Steine setzen
        for spalte in range(SPALTEN):
            btn = tk.Button(root, text=str(spalte + 1), width=4, command=lambda s=spalte: self.chip_setzen(s))
            btn.grid(row=1, column=spalte, padx=2, pady=4)

        self.zeichne_feld()

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

    def chip_setzen(self, spalte):
        for zeile in reversed(range(REIHEN)):
            if self.feld[zeile][spalte] == " ":
                self.feld[zeile][spalte] = self.spieler
                self.zeichne_feld()
                if self.spielfeld_voll():
                    self.canvas.create_text(
                        (SPALTEN * ZELL_GROESSE) // 2, 
                        (REIHEN * ZELL_GROESSE) // 2,
                        text="Unentschieden!", font=("Arial", 24), fill="white"
                    )
                else:
                    self.spieler = "O" if self.spieler == "X" else "X"
                return
        print("Spalte voll!")  # Optional: Fehleranzeige für volle Spalte

    def spielfeld_voll(self):
        return all(self.feld[0][spalte] != " " for spalte in range(SPALTEN))

# Fenster starten
fenster = tk.Tk()
spiel = VierGewinntGUI(fenster)
fenster.mainloop()
