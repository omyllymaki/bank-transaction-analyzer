from abc import abstractmethod
from typing import Union, Tuple

from PyQt5.QtWidgets import QLineEdit


class TextLineEdit(QLineEdit):

    def __init__(self, *args):
        super().__init__(*args)

    def get_value(self) -> Union[str, None]:
        """
        Get content of field as str.
        Return str value or None if not set.
        """

        text = super().text()
        if text == "":
            return None
        else:
            return text


class NumericLineEdit(QLineEdit):

    def __init__(self, *args, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(*args)

    def get_value(self) -> Tuple[Union[float, int, None], bool]:
        """
        Get content of field as numeric value.
        Return numeric value and is_valid boolean

        Empty string -> None, True
        Invalid string -> none, False
        Value not within boundaries -> None, False
        Value within boundaries -> float, True
        """

        text = super().text()
        if text == "":
            self._set_white_background()
            return None, True

        try:
            value = self.text_to_value(text)
        except Exception as e:
            print(e)
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

    @abstractmethod
    def text_to_value(self, text):
        raise NotImplementedError

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


class FloatLineEdit(NumericLineEdit):

    def __init__(self, *args, min_value=None, max_value=None):
        super().__init__(*args, min_value=min_value, max_value=max_value)

    def text_to_value(self, text):
        return float(text)


class IntLineEdit(NumericLineEdit):

    def __init__(self, *args, min_value=None, max_value=None):
        super().__init__(*args, min_value=min_value, max_value=max_value)

    def text_to_value(self, text):
        return int(text)
