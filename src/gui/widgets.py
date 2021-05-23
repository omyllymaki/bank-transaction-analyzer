from typing import Union, Tuple

from PyQt5.QtWidgets import QLineEdit


class FloatLineEdit(QLineEdit):

    def __init__(self, *args, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(*args)

    def get_value(self) -> Tuple[Union[float, None], bool]:
        """
        Get content of field as float.
        Return float value and is_valid boolean

        Empty string -> None, True
        Invalid string -> none, False
        Float not within boundaries -> None, False
        Float within boundaries -> float, True
        """

        text = super().text()
        if text == "":
            self._set_white_background()
            return None, True

        try:
            value = float(text)
        except Exception:
            self._set_red_background()
            return None, False

        if self.min_value is not None:
            if value < self.min_value:
                self._set_red_background()
                return None, False

        if self.max_value is not None:
            if value > self.max_value:
                self._set_red_background()
                return None, False

        self._set_white_background()
        return value, True

    def _set_red_background(self):
        self.setStyleSheet("QLineEdit"
                           "{"
                           "background : red;"
                           "}")

    def _set_white_background(self):
        self.setStyleSheet("QLineEdit"
                           "{"
                           "background : white;"
                           "}")
