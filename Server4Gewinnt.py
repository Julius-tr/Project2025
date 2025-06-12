# Import der benötigten Module
import socket             # Ermöglicht Netzwerkverbindungen (TCP/IP)
import threading          # Ermöglicht paralleles Ausführen von Code (für Nachrichtenaustausch)
import tkinter as tk      # Modul für die grafische Benutzeroberfläche
from Code4Gewinnt import VierGewinntGUI  # Importiert die Spielfeld- und Spiel-Logik
import os                 # Modul zur Arbeit mit dem Dateisystem (Dateiprüfung etc.)

# Server-IP: leerer String akzeptiert Verbindungen von jeder IP-Adresse
HOST = ''
PORT = 12345  # Fester Port, auf dem der Server lauscht

# Dateiname, in dem die Siege gespeichert werden
SIEGE_DATEI = "siege_Server.txt"

# Funktion zum Laden der Siege aus der Datei
def lade_siege():
    # Wenn Datei nicht existiert, Standard-Sieganzahl zurückgeben
    if not os.path.exists(SIEGE_DATEI):
        return {"Server": 0, "Client": 0}
    # Datei zeilenweise lesen
    with open(SIEGE_DATEI, "r") as f:
        inhalt = f.read().splitlines()
    siege = {"Server": 0, "Client": 0}
    # Je zwei Zeilen pro Spieler (Name + Anzahl)
    for i in range(0, len(inhalt), 2):
        if i+1 < len(inhalt):
            name = inhalt[i].replace(":", "")  # Entferne ":" nach dem Namen
            anzahl = int(inhalt[i+1])          # Konvertiere Sieganzahl zu int
            siege[name] = anzahl               # Speichere im Dictionary
    return siege

# Funktion zum Speichern eines Sieges für den angegebenen Gewinner
def speichere_sieg(gewinner):  # erwartet "Server" oder "Client"
    siege = lade_siege()        # Lade aktuelle Statistik
    siege[gewinner] += 1        # Erhöhe Sieganzahl des Gewinners
    # Schreibe aktualisierte Werte in die Datei
    with open(SIEGE_DATEI, "w") as f:
        f.write(f"Server:\n{siege['Server']}\nClient:\n{siege['Client']}\n")

# Klasse für das Netzwerkspiel, erweitert die grafische Spieloberfläche
class NetzwerkSpiel(VierGewinntGUI):
    def __init__(self, root, verbindung, ist_server=False):
        super().__init__(root)  # Initialisiere die GUI von der Basisklasse
        self.verbindung = verbindung
        self.ist_server = ist_server
        # Setze Fenster-Titel abhängig davon, ob es Server oder Client ist
        self.root.title("4 Gewinnt – " + ("Server (Rot)" if ist_server else "Client (Gelb)"))
        self.spieler = "X" if ist_server else "O"  # Server ist Rot (X), Client ist Gelb (O)
        self.dran = ist_server  # Server beginnt mit dem ersten Zug

        # Starte einen neuen Thread, der eingehende Nachrichten vom Netzwerk empfängt
        threading.Thread(target=self.empfange_nachrichten, daemon=True).start()

        # Weise dem Reset-Button eine eigene Funktion zu (auch Netzwerk-Reset)
        self.reset_button.config(command=self.sende_neustart)

    # Wenn Spieler einen Chip setzen möchte
    def chip_setzen(self, spalte):
        # Abbrechen, wenn nicht an der Reihe oder Spiel inaktiv
        if not self.dran or not self.spiel_aktiv:
            return
        # Abbrechen, wenn oberste Zelle der Spalte belegt ist (Spalte voll)
        if self.feld[0][spalte] != " ":
            return

        # Kopiere aktuellen Spielfeld-Zustand vor dem Zug
        vorheriger_status = [reihe[:] for reihe in self.feld]
        super().chip_setzen(spalte)  # Führe Chip-Setzen durch (GUI und Logik)

        # Wenn das Spiel nach dem Zug vorbei ist (Sieg) und sich das Feld verändert hat
        if not self.spiel_aktiv and vorheriger_status != self.feld:
            if self.dran:
                gewinner = "Server"
            else:
                gewinner = "Client"
            speichere_sieg(gewinner)  # Sieg speichern

        # Sende den gespielten Zug (Spaltennummer) an den Client
        try:
            self.verbindung.sendall(str(spalte).encode())
        except:
            pass  # Sende-Fehler ignorieren (z. B. Verbindung verloren)

        self.dran = False  # Gegner ist nun an der Reihe

    # Funktion, die permanent Nachrichten vom Client empfängt
    def empfange_nachrichten(self):
        while True:
            try:
                daten = self.verbindung.recv(1024)  # Empfange bis zu 1024 Bytes
                if not daten:
                    break  # Wenn keine Daten mehr ankommen, Verbindung beendet
                nachricht = daten.decode()  # Dekodiere empfangene Nachricht
                if nachricht == "RESET":
                    # Starte das Spiel im GUI-Thread neu
                    self.root.after(0, self.spiel_neustarten)
                else:
                    # Empfange Zug (Spaltennummer) und spiele ihn im GUI-Thread
                    spalte = int(nachricht)
                    self.root.after(0, lambda: self.netzwerk_zug(spalte))
            except:
                break  # Fehler beim Empfang oder Verbindung verloren

    # Wird aufgerufen, wenn der Gegner (Client) einen Chip setzt
    def netzwerk_zug(self, spalte):
        vorheriger_status = [reihe[:] for reihe in self.feld]
        super().chip_setzen(spalte)  # Führe den gegnerischen Zug aus

        # Wenn das Spiel nach dem gegnerischen Zug vorbei ist
        if not self.spiel_aktiv and vorheriger_status != self.feld:
            if self.dran:
                gewinner = "Server"
            else:
                gewinner = "Client"
            speichere_sieg(gewinner)  # Sieg speichern

        self.dran = True  # Spieler ist wieder dran

    # Sende einen "RESET"-Befehl an den Gegner und starte lokal neu
    def sende_neustart(self):
        self.spiel_neustarten()  # Lokales Zurücksetzen
        try:
            self.verbindung.sendall("RESET".encode())  # Sende RESET an Client
        except:
            pass  # Fehler beim Senden ignorieren

# === Hauptteil: Server starten und GUI starten ===

# Erstelle einen TCP/IP-Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Binde den Socket an die IP-Adresse und den Port
server_socket.bind((HOST, PORT))

# Warte auf genau eine eingehende Verbindung
server_socket.listen(1)
print("Warte auf Verbindung...")

# Sobald ein Client sich verbindet, akzeptiere die Verbindung
verbindung, adresse = server_socket.accept()
print(f"Verbunden mit {adresse}")

# Starte die grafische Benutzeroberfläche (GUI)
fenster = tk.Tk()
spiel = NetzwerkSpiel(fenster, verbindung, ist_server=True)  # Erstelle ein Spielobjekt für den Server
fenster.mainloop()  # Starte die Ereignisschleife (GUI bleibt offen)

