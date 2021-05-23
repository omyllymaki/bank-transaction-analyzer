from PyQt5.QtWidgets import QMessageBox


def show_warning(title: str, text: str = ""):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(QMessageBox.Ok)
    return msg.exec_()
