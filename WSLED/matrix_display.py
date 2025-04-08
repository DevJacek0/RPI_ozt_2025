from luma.core.interface.serial import spi, noop
from luma.led_matrix.device import max7219
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, LCD_FONT


class MatrixDisplay:
    def __init__(self, cascaded=4, block_orientation=-90, scroll_delay=0.05, font=None):
        """
        Inicjalizuje wyświetlacz LED matrix.

        :param cascaded: Liczba połączonych modułów LED
        :param block_orientation: Orientacja bloków (domyślnie -90)
        :param scroll_delay: Opóźnienie przewijania tekstu
        :param font: Czcionka do użycia (domyślnie LCD_FONT)

        return: None
        """


        self.serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(self.serial, cascaded=cascaded, block_orientation=block_orientation)
        self.scroll_delay = scroll_delay
        self.font = font or proportional(LCD_FONT)

    def clear(self):
        """
        Czyści ekran.
        """
        self.device.clear()

    def show(self, msg, scroll=True, delay=None, font=None):
        """
        Wyświetla tekst na ekranie.

        :param msg: Tekst do wyświetlenia
        :param scroll: Czy przewijać tekst (jeśli False, tekst się nie przesuwa)
        :param delay: Opóźnienie scrollowania
        :param font: Czcionka (opcjonalnie)

        return: None
        """
        if scroll:
            show_message(
                self.device,
                msg,
                fill="white",
                font=font or self.font,
                scroll_delay=delay or self.scroll_delay
            )
        else:
            from luma.core.legacy import text
            from luma.core.render import canvas
            with canvas(self.device) as draw:
                text(draw, (0, 0), msg, fill="white", font=font or self.font)
