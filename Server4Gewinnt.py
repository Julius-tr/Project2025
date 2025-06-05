import socket
import threading
import tkinter as tk
from Code4Gewinnt import VierGewinntGUI

HOST = ''  # Server akzeptiert Verbindungen von überall
PORT = 12345

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
        super().chip_setzen(spalte)
        self.verbindung.sendall(str(spalte).encode())
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
        super().chip_setzen(spalte)
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
