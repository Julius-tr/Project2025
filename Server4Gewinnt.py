import socket
import threading
import tkinter as tk
from Code4Gewinnt import VierGewinntGUI

HOST = ''  # Server akzeptiert Verbindungen von überall
PORT = 12345

class NetzwerkSpiel(VierGewinntGUI):
    def __init__(self, root, verbindung, ist_server=True):
        super().__init__(root)
        self.verbindung = verbindung
        self.ist_server = ist_server
        self.root.title("4 Gewinnt – Server (Rot (beginnt))")
        self.spieler = "X" if ist_server else "O"
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