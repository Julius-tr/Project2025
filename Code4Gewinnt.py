'''
Dies wird/ist ein 4 Gewinnt Multiplayer per sockets code
Creators:
    Julia
    Matteo
Prüfstelle:
    HTL-Anichstrasse
'''

#Anzahl der Reihen uns Spalten
REIHEN = 6
SPALTEN = 7

#Spielfeld erstellen
Feld = [[" " for i in range(SPALTEN)] for i in range(REIHEN)]

def print_Feld(Feld):
    print("\nSpielfeld:")
    for reihe in Feld:
        print("| " + " | ".join(reihe) + " |")
    print("   " + "   ".join(str(i+1) for i in range(SPALTEN)))

def Chip_setzen(Feld, spalte, chip):
#Startet von unten und sucht die erste freie Zeile
    for reihe in reversed(range(REIHEN)):
        if Feld[reihe][spalte] == " ":
            Feld[reihe][spalte] = chip
            return True
    return False  #die Spalte ist voll

def voll(Feld):
    return all(Feld[0][spalte] != " " for spalte in range(SPALTEN))

#Spiel starten
Spieler = "X"

while True:
    print_Feld(Feld)
    try:
        spalte_input = int(input(f"Spieler {Spieler}, wähle eine Spalte (1–7): ")) - 1
        if 0 <= spalte_input < SPALTEN:
            if Chip_setzen(Feld, spalte_input, Spieler):
        # Spieler wechseln
                Spieler = "O" if Spieler == "X" else "X"
            else:
                print("Diese Spalte ist voll. Bitte wähle eine andere.")
        else:
            print("Ungültige Spalte. Nur 1 bis 7.")
    except ValueError:
        print("Bitte gib eine Zahl ein.")

    if voll(Feld):
        print_Feld(Feld)
        print("Das Spielfeld ist voll – unentschieden!")
        break
