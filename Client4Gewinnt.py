import socket
import threading
import tkinter as tk
from Code4Gewinnt import VierGewinntGUI

SERVER_IP = input("Gib die IP-Adresse des Servers ein: ")  # ÄNDERN: IP des Servers
PORT = 12345

class NetzwerkSpiel(VierGewinntGUI):
    def __init__(self, root, verbindung, ist_server=False):
        super().__init__(root)
        self.verbindung = verbindung
        self.ist_server = ist_server
        self.root.title("4 Gewinnt – Client (Gelb)")
        self.spieler = "O" if ist_server else "X"
        self.dran = ist_server  # Nur der Server beginnt

        # Netzwerk-Thread starten
        threading.Thread(target=self.empfange_zug, daemon=True).start()

    def chip_setzen(self, spalte):
        if not self.dran or not self.spiel_aktiv:
            return
        super().chip_setzen(spalte)
        self.verbindung.sendall(str(spalte).encode())
        self.dran = False

    def empfange_zug(self):
        while True:
            try:
                daten = self.verbindung.recv(1024)
                if not daten:
                    break
                spalte = int(daten.decode())
                self.root.after(0, lambda: self.netzwerk_zug(spalte))
            except:
                break

    def netzwerk_zug(self, spalte):
        super().chip_setzen(spalte)
        self.dran = True

#Verbindung zum Server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))
print("Verbunden mit Server")

#GUI starten
fenster = tk.Tk()
spiel = NetzwerkSpiel(fenster, client_socket, ist_server=False)
fenster.mainloop()
