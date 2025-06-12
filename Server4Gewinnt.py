import socket
import threading
import tkinter as tk
from Code4Gewinnt import VierGewinntGUI
import os

HOST = ''  # Server akzeptiert Verbindungen von überall
PORT = 12345

SIEGE_DATEI = "siege_Server.txt"

def lade_siege():
    if not os.path.exists(SIEGE_DATEI):
        return {"Server": 0, "Client": 0}
    with open(SIEGE_DATEI, "r") as f:
        inhalt = f.read().splitlines()
    siege = {"Server": 0, "Client": 0}
    for i in range(0, len(inhalt), 2):
        if i+1 < len(inhalt):
            name = inhalt[i].replace(":", "")
            anzahl = int(inhalt[i+1])
            siege[name] = anzahl
    return siege

def speichere_sieg(gewinner):  # "Server" oder "Client"
    siege = lade_siege()
    siege[gewinner] += 1
    with open(SIEGE_DATEI, "w") as f:
        f.write(f"Server:\n{siege['Server']}\nClient:\n{siege['Client']}\n")

class NetzwerkSpiel(VierGewinntGUI):
    def __init__(self, root, verbindung, ist_server=False):
        super().__init__(root)
        self.verbindung = verbindung
        self.ist_server = ist_server
        self.root.title("4 Gewinnt – " + ("Server (Rot)" if ist_server else "Client (Gelb)"))
        self.spieler = "X" if ist_server else "O"
        self.dran = ist_server  # Server beginnt

        threading.Thread(target=self.empfange_nachrichten, daemon=True).start()

        # Button anpassen
        self.reset_button.config(command=self.sende_neustart)

    def chip_setzen(self, spalte):
        if not self.dran or not self.spiel_aktiv:
            return
        if self.feld[0][spalte] != " ":
            return

        vorheriger_status = [reihe[:] for reihe in self.feld]  # Spielfeld vorher kopieren
        super().chip_setzen(spalte)

        if not self.spiel_aktiv and vorheriger_status != self.feld:
            if self.dran:
                gewinner = "Server" 
            else:
                gewinner = "Client"
            speichere_sieg(gewinner)

        try:
            self.verbindung.sendall(str(spalte).encode())
        except:
            pass

        self.dran = False

    def empfange_nachrichten(self):
        while True:
            try:
                daten = self.verbindung.recv(1024)
                if not daten:
                    break
                nachricht = daten.decode()
                if nachricht == "RESET":
                    self.root.after(0, self.spiel_neustarten)
                else:
                    spalte = int(nachricht)
                    self.root.after(0, lambda: self.netzwerk_zug(spalte))
            except:
                break

    def netzwerk_zug(self, spalte):
        vorheriger_status = [reihe[:] for reihe in self.feld]
        super().chip_setzen(spalte)

        if not self.spiel_aktiv and vorheriger_status != self.feld:
            if self.dran:
                gewinner = "Server"
            else:
                gewinner = "Client"
            speichere_sieg(gewinner)

        self.dran = True

    def sende_neustart(self):
        self.spiel_neustarten()
        try:
            self.verbindung.sendall("RESET".encode())
        except:
            pass


# Server-Socket starten
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Warte auf Verbindung...")

verbindung, adresse = server_socket.accept()
print(f"Verbunden mit {adresse}")

# GUI starten
fenster = tk.Tk()
spiel = NetzwerkSpiel(fenster, verbindung, ist_server=True)
fenster.mainloop()
