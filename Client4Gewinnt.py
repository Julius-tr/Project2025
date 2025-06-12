# Importiere notwendige Module
import socket             # Für Netzwerkverbindungen (TCP/IP)
import threading          # Für paralleles Ausführen von Funktionen (z. B. Nachricht empfangen)
import tkinter as tk      # Für die grafische Benutzeroberfläche
from Code4Gewinnt import VierGewinntGUI  # Importiert die Spiellogik und Oberfläche
import os                 # Für Dateisystemoperationen (z. B. Datei existiert?)

# Abfrage der Server-IP beim Benutzer
SERVER_IP = input("Gib die IP-Adresse des Servers ein: ")  # Benutzer muss IP des Servers eingeben
PORT = 12345  # Fester Port, auf dem der Server lauscht

# Name der Datei, in der die Siege gespeichert werden
SIEGE_DATEI = "siege_Client.txt"

# Funktion zum Laden der bisherigen Siege aus Datei
def lade_siege():
    if not os.path.exists(SIEGE_DATEI):  # Wenn Datei nicht existiert, Standardwerte verwenden
        return {"Server": 0, "Client": 0}
    with open(SIEGE_DATEI, "r") as f:  # Datei öffnen und lesen
        inhalt = f.read().splitlines()  # Zeilenweise lesen
    siege = {"Server": 0, "Client": 0}  # Dictionary zur Speicherung
    for i in range(0, len(inhalt), 2):  # Alle zwei Zeilen: Name + Zahl
        if i+1 < len(inhalt):
            name = inhalt[i].replace(":", "")  # ":" vom Namen entfernen
            anzahl = int(inhalt[i+1])          # Anzahl der Siege
            siege[name] = anzahl               # Im Dictionary speichern
    return siege

# Funktion zum Speichern eines Sieges in die Datei
def speichere_sieg(gewinner):  # "Server" oder "Client"
    siege = lade_siege()       # Aktuelle Siege laden
    siege[gewinner] += 1       # Sieg des entsprechenden Spielers erhöhen
    with open(SIEGE_DATEI, "w") as f:  # Datei überschreiben
        f.write(f"Server:\n{siege['Server']}\nClient:\n{siege['Client']}\n")  # Formatierter Output

# Klasse für das Netzwerkspiel – erweitert die GUI mit Netzwerkanbindung
class NetzwerkSpiel(VierGewinntGUI):
    def __init__(self, root, verbindung, ist_server=False):
        super().__init__(root)  # GUI initialisieren
        self.verbindung = verbindung  # Socket-Verbindung speichern
        self.ist_server = ist_server  # Merken, ob Server oder Client
        self.root.title("4 Gewinnt – " + ("Server (Rot)" if ist_server else "Client (Gelb)"))  # Fenster-Titel
        self.spieler = "O" if ist_server else "X"  # Spieler-Symbol setzen
        self.dran = ist_server  # Server beginnt immer

        # Starte einen Thread zum Empfang von Nachrichten
        threading.Thread(target=self.empfange_nachrichten, daemon=True).start()

        # Weist dem "Neustart"-Button eine neue Funktion zu
        self.reset_button.config(command=self.sende_neustart)

    # Aktion bei eigenem Spielzug
    def chip_setzen(self, spalte):
        if not self.dran or not self.spiel_aktiv:  # Wenn nicht dran oder Spiel vorbei, abbrechen
            return
        if self.feld[0][spalte] != " ":  # Wenn Spalte voll ist, abbrechen
            return

        vorheriger_status = [reihe[:] for reihe in self.feld]  # Spielfeld vor dem Zug speichern (für Sieganalyse)
        super().chip_setzen(spalte)  # Chip im Spielfeld setzen

        # Wenn nach dem Zug das Spiel vorbei ist (Sieg) und das Feld sich verändert hat
        if not self.spiel_aktiv and vorheriger_status != self.feld:
            if self.dran:  # Wenn ich dran war, habe ich gewonnen
                gewinner = "Client"
            else:
                gewinner = "Server"
            speichere_sieg(gewinner)  # Sieg speichern

        # Zug (Spaltennummer) an den Server senden
        try:
            self.verbindung.sendall(str(spalte).encode())
        except:
            pass  # Fehler beim Senden ignorieren

        self.dran = False  # Jetzt ist der andere Spieler dran

    # Empfang von Nachrichten vom Netzwerk (Zug oder Reset)
    def empfange_nachrichten(self):
        while True:
            try:
                daten = self.verbindung.recv(1024)  # Bis zu 1024 Byte empfangen
                if not daten:  # Wenn nichts empfangen wurde, Verbindung verloren
                    break
                nachricht = daten.decode()  # Nachricht decodieren
                if nachricht == "RESET":
                    self.root.after(0, self.spiel_neustarten)  # Spiel im GUI-Thread zurücksetzen
                else:
                    spalte = int(nachricht)  # Spaltennummer des Zugs
                    self.root.after(0, lambda: self.netzwerk_zug(spalte))  # Im GUI-Thread verarbeiten
            except:
                break  # Bei Fehler: Verbindung schließen

    # Verarbeite gegnerischen Zug
    def netzwerk_zug(self, spalte):
        vorheriger_status = [reihe[:] for reihe in self.feld]  # Spielfeld vor dem Zug speichern
        super().chip_setzen(spalte)  # Chip setzen

        # Wenn Spiel nach dem Zug vorbei ist, Sieger bestimmen
        if not self.spiel_aktiv and vorheriger_status != self.feld:
            if self.dran:  # Wenn ich dran war, habe ich verloren
                gewinner = "Client"
            else:
                gewinner = "Server"
            speichere_sieg(gewinner)

        self.dran = True  # Ich bin jetzt wieder dran

    # Funktion zum Neustarten des Spiels und Senden an den Gegner
    def sende_neustart(self):
        self.spiel_neustarten()  # Lokales Spielfeld zurücksetzen
        try:
            self.verbindung.sendall("RESET".encode())  # Befehl an den Gegner senden
        except:
            pass  # Fehler ignorieren

# Verbindung zum Server herstellen
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket erstellen
client_socket.connect((SERVER_IP, PORT))  # Verbindung zum Server aufbauen
print("Verbunden mit Server")

# GUI starten
fenster = tk.Tk()
spiel = NetzwerkSpiel(fenster, client_socket, ist_server=False)  # Client-Spiel starten
fenster.mainloop()  # GUI-Hauptschleife starten

