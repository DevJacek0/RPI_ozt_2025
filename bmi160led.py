# Połączenie czujnika BMI160:
# BMI160 - Raspberry Pi
# VIN	3.3V
# GND	GND
# SCL	SCL1 GPIO 3
# SDA	SDA1 GPIO 2
# CS	3.3V
# SAO	GND (adrs na 0x68)
# Port 1, 0x68

# Połączenie wyświetlacza LED:
# MAX7219 - Raspberry Pi
# VCC	5V
# GND	GND
# DIN	GPIO 10 (MOSI)
# CLK	GPIO 11 (SCK)
# CS	GPIO 8 (CE0)



from time import sleep
import os
from BMI160_i2c import Driver
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219


class SensorManager:
    """BMI160 Sensor Manager"""

    def __init__(self, address=0x68):
        self.sensor = Driver(address)

    def get_motion_data(self):
        """Pobiera dane z czujnika ruchu"""
        return self.sensor.getMotion6()


class DisplayManager:
    """Klasa bazowa dla wyświetlacza"""

    def __init__(self, grid_size=9):
        self.grid_size = grid_size

    def scale_value(self, value, scale_factor=20000):
        """Skaluje wartość akcelerometru do pozycji na siatce"""
        max_index = (self.grid_size - 1) // 2
        pos = int((value / scale_factor) * max_index)
        return max(min(pos, max_index), -max_index)


class ConsoleDisplay(DisplayManager):
    """Wyświetlacz konsolowy"""

    def clear(self):
        """Czyści konsolę"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_data(self, motion_data):
        """Wyświetla dane ruchu w konsoli"""
        gx, gy, gz, ax, ay, az = motion_data

        self.clear()
        print("=== ORIENTACJA BMI160 ===")
        print(f"Akcelerometr: ax={ax}, ay={ay}, az={az}")
        print(f"Żyroskop:     gx={gx}, gy={gy}, gz={gz}")
        print()
        self._draw_grid(ax, ay)

    def _draw_grid(self, ax, ay):
        """Rysuje siatkę 2D z kursorem pokazującym orientację"""
        x = self.scale_value(ay)
        y = self.scale_value(ax)

        center = (self.grid_size - 1) // 2
        for row in range(self.grid_size):
            line = ""
            for col in range(self.grid_size):
                if row == center - y and col == center + x:
                    line += "🞄"
                elif row == center and col == center:
                    line += "+"
                else:
                    line += "."
            print(line)


class LedMatrixDisplay(DisplayManager):
    """Wyświetlacz matrycy LED"""

    def __init__(self, matrix_size=8, port=0, device_num=0, cascaded=4, orientation=-90):
        super().__init__()
        self.matrix_size = matrix_size
        serial = spi(port=port, device=device_num, gpio=noop())
        self.device = max7219(serial, cascaded=cascaded, block_orientation=orientation)
        self.device.clear()

    def scale_value(self, value, scale_factor=20000):
        """Skaluje wartość czujnika do współrzędnych matrycy LED"""
        half_size = self.matrix_size / 2
        pos = (value / scale_factor) * (half_size - 1)
        return int(half_size + pos)

    def show_data(self, motion_data):
        """Wyświetla dane ruchu na matrycy LED"""
        _, _, _, ax, ay, _ = motion_data

        with canvas(self.device) as draw:
            x = self.scale_value(ay)
            y = self.scale_value(ax)

            # odniesienie centrum
            draw.point((16, 4), fill="white")

            # kropa pokazująca orientację
            draw.point((x, y), fill="white")

    def clear(self):
        """Czyści wyświetlacz LED"""
        self.device.clear()


class OrientationMonitor:
    """Główna klasa aplikacji monitorującej orientację"""

    def __init__(self, update_delay=0.2):
        self.update_delay = update_delay
        self.running = False

    def setup(self):
        """Inicjalizuje komponenty systemu"""
        print("Inicjalizacja czujnika BMI160")
        self.sensor = SensorManager()

        print("Inicjalizacja matrycy LED")
        self.led_display = LedMatrixDisplay()

        self.console_display = ConsoleDisplay()
        print("Inicjalizacja zakonczona pomyslnie")

    def run(self):
        """Uruchamia główną pętlę programu"""
        self.running = True

        try:
            while self.running:
                # Pobranie danych z czujnika
                motion_data = self.sensor.get_motion_data()

                # Aktualizacja wyświetlaczy
                self.console_display.show_data(motion_data)
                self.led_display.show_data(motion_data)

                # Opóźnienie aktualizacji
                sleep(self.update_delay)

        except KeyboardInterrupt:
            print("\nZatrzymano test.")
        finally:
            self.cleanup()

    def cleanup(self):
        """Zwalnia zasoby przy zakończeniu"""
        if hasattr(self, 'led_display'):
            self.led_display.clear()
        self.running = False


if __name__ == "__main__":
    monitor = OrientationMonitor()
    monitor.setup()
    monitor.run()