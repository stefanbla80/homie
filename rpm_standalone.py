import gpiozero
import time
import datetime

TACHO_PIN = gpiozero.Button(24)

class Tacho:
    def __init__(self):
        self.startzeit = None
        self.zaehler = 0
        self.messung = 0
        self.messung_old = datetime.datetime.now()

    def start_frequenzzaehlung(self):
        TACHO_PIN.when_pressed = self.zaehler_erhoehen
        self.startzeit = datetime.datetime.now()

    def stop_frequenzzaehlung(self):
        TACHO_PIN.when_pressed = None
        self.ergebnisse_auswerten()
        self.zaehler = 0

    def zaehler_erhoehen(self):
        now = datetime.datetime.now()
        self.messung = (now - self.messung_old).total_seconds()
        self.messung_old = now
        self.zaehler += 1

    def ergebnisse_auswerten(self):
        try:
            messung = 1 / self.messung
        except ZeroDivisionError:
            messung = 0
        if messung >= 100:
           # print(f"Zählung: {self.zaehler}")
            rpm = self.zaehler / 2 * 60
        else:
            #print(f"Messung: {messung}")
            rpm = messung / 2 * 60
            #rpm = 0
        #print(f"RPM: {rpm}")
        print(rpm)

def main():
    tacho = Tacho()
    while True:
        tacho.start_frequenzzaehlung()
        while (datetime.datetime.now() - tacho.startzeit).total_seconds() < 1:
            time.sleep(0.02)
        tacho.stop_frequenzzaehlung()
        time.sleep(1)

if __name__ == "__main__":
    main()