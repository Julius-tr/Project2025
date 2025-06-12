'''
Dies ist ein Code für das Spielfeld von 4 Gewinnt, welches mit den Codes Client4Gewinnt und Server4Gewinnt per sockets spielbar ist.
Creators:
    Julia
    Matteo
Prüfstelle:
    HTL-Anichstrasse
'''

import tkinter as tk  # Importiere das GUI-Modul

# Konstanten für das Spielfeld
REIHEN = 6                     # Anzahl der Zeilen im Spielfeld
SPALTEN = 7                    # Anzahl der Spalten im Spielfeld
ZELL_GROESSE = 60              # Größe jeder Zelle in Pixel

# Farbcodes für die Spielerchips und leere Zellen
FARBEN = {"X": "#f13914", "O": "#e6e51d", " ": "#f1f1f1"}  # Rot, Gelb, Weiß
NAMEN = {"X": "Rot", "O": "Gelb"}  # Spielername zur Anzeige

# GUI-Klasse für 4 Gewinnt
class VierGewinntGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("4 Gewinnt – Julia & Matteo")  # Fenstertitel setzen

        # Button zum Neustarten des Spiels
        self.reset_button = tk.Button(root, text="Spiel Neustarten", command=self.spiel_neustarten)
        self.reset_button.grid(row=2, column=0, columnspan=SPALTEN, pady=10)

        # 2D-Liste zur Darstellung des Spielfelds (initial leer)
        self.feld = [[" " for _ in range(SPALTEN)] for _ in range(REIHEN)]

        self.spieler = "X"         # Startspieler ist "X" (Rot)
        self.spiel_aktiv = True    # Spiel ist aktiv (nicht vorbei)

        # Erstelle das Spielfeld-Canvas (Zeichenbereich)
        self.canvas = tk.Canvas(root, width=SPALTEN * ZELL_GROESSE, height=REIHEN * ZELL_GROESSE, bg="#1207c1")
        self.canvas.grid(row=1, column=0, columnspan=SPALTEN)

        self.buttons = []  # Liste für die Steine-Setz-Buttons (oben)

        # Erstelle Buttons für jede Spalte
        for spalte in range(SPALTEN):
            btn = tk.Button(root, text=str(spalte + 1), width=4, command=lambda s=spalte: self.chip_setzen(s))
            btn.grid(row=0, column=spalte, padx=2, pady=4)

            # Hovereffekt: wenn Maus über Button → "O" anzeigen, sonst Spaltennummer
            btn.bind("<Enter>", lambda e, s=spalte: self.hover_begin(e, s))
            btn.bind("<Leave>", lambda e, s=spalte: self.hover_ende(e, s))

            self.buttons.append(btn)

        self.zeichne_feld()       # Zeichne das leere Spielfeld
        self.status_text_id = None  # Für spätere Statusanzeige im Canvas

    # Hover-Effekt starten: Chip-Vorschau anzeigen
    def hover_begin(self, event, spalte):
        if self.spiel_aktiv and self.feld[0][spalte] == " ":
            event.widget.config(text="O", fg="black", font=("Arial", 10, "bold"), bg=FARBEN[self.spieler])

    # Hover-Effekt beenden: Button auf ursprüngliche Anzeige zurücksetzen
    def hover_ende(self, event, spalte):
        if self.spiel_aktiv:
            event.widget.config(text=str(spalte + 1), fg="black", font=("Arial", 10), bg="SystemButtonFace")

    # Status-Text (Sieg/Unentschieden) in der Mitte des Canvas anzeigen
    def zeige_status_text(self, text, farbe="black"):
        if self.status_text_id:
            self.canvas.delete(self.status_text_id)  # Vorherigen Text entfernen

        # Position für die Anzeige (zentriert im Spielfeld)
        x = (SPALTEN * ZELL_GROESSE) // 2
        y = (REIHEN * ZELL_GROESSE) // 2

        # Hintergrund-Rechteck
        self.canvas.create_rectangle(x - 160, y - 40, x + 160, y + 40, fill="white", outline="black", width=3)

        # Text selbst
        self.status_text_id = self.canvas.create_text(x, y, text=text, fill=farbe, font=("Arial", 24, "bold"))

    # Zeichnet alle Chips auf dem Canvas entsprechend dem Spielfeldzustand
    def zeichne_feld(self):
        self.canvas.delete("all")  # Canvas leeren
        for zeile in range(REIHEN):
            for spalte in range(SPALTEN):
                x1 = spalte * ZELL_GROESSE + 5
                y1 = zeile * ZELL_GROESSE + 5
                x2 = x1 + ZELL_GROESSE - 10
                y2 = y1 + ZELL_GROESSE - 10
                farbe = FARBEN[self.feld[zeile][spalte]]
                self.canvas.create_oval(x1, y1, x2, y2, fill=farbe, outline="black")

    # Setzt das Spielfeld zurück und beginnt ein neues Spiel
    def spiel_neustarten(self):
        self.feld = [[" " for _ in range(SPALTEN)] for _ in range(REIHEN)]
        self.spieler = "X"
        self.spiel_aktiv = True
        self.zeichne_feld()

    # Setzt einen Chip in die gewünschte Spalte
    def chip_setzen(self, spalte):
        if not self.spiel_aktiv:
            return

        gesetzt = False
        for zeile in reversed(range(REIHEN)):  # Von unten nach oben suchen
            if self.feld[zeile][spalte] == " ":
                self.feld[zeile][spalte] = self.spieler
                self.zeichne_feld()
                gesetzt = True

                # Gewinn prüfen
                if self.pruefe_gewinner(zeile, spalte):
                    self.canvas.create_text(
                        (SPALTEN * ZELL_GROESSE) // 2,
                        (REIHEN * ZELL_GROESSE) // 2,
                        text=f"Spieler {NAMEN[self.spieler]} \n gewinnt!",
                        font=("Arial", 32, "bold"), fill="green"
                    )
                    self.spiel_aktiv = False
                    return

                # Unentschieden prüfen
                elif self.spielfeld_voll():
                    self.canvas.create_text(
                        (SPALTEN * ZELL_GROESSE) // 2,
                        (REIHEN * ZELL_GROESSE) // 2,
                        text="Unentschieden!",
                        font=("Arial", 24), fill="white"
                    )
                    self.spiel_aktiv = False
                    return

                # Spieler wechseln
                else:
                    self.spieler = "O" if self.spieler == "X" else "X"
                return

        print("Spalte voll!")  # Falls kein Chip gesetzt werden konnte

    # Prüft, ob das Spielfeld voll ist (für Unentschieden)
    def spielfeld_voll(self):
        return all(self.feld[0][spalte] != " " for spalte in range(SPALTEN))

    # Prüft, ob der letzte gesetzte Chip zu einem Sieg geführt hat
    def pruefe_gewinner(self, zeile, spalte):
        # Funktion zählt gleiche Chips in eine Richtung
        def zaehle_richtung(dz, ds):
            count = 0
            z, s = zeile + dz, spalte + ds
            while 0 <= z < REIHEN and 0 <= s < SPALTEN and self.feld[z][s] == self.spieler:
                count += 1
                z += dz
                s += ds
            return count

        # Richtungen: horizontal, vertikal, diagonal ↘, diagonal ↙
        richtungen = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dz, ds in richtungen:
            count = 1 + zaehle_richtung(dz, ds) + zaehle_richtung(-dz, -ds)
            if count >= 4:
                return True  # Sieger gefunden
        return False  # Kein Sieg

