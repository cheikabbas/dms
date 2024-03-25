from PyQt5.QtWidgets import QMessageBox


def show_info_messagebox(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    # setting message for Message Box
    msg.setText(text)

    # setting Message box window title
    msg.setWindowTitle("Information")

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok)

    # start the app
    msg.exec_()


def show_warning_messagebox(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)

    # setting message for Message Box
    msg.setText(text)

    # setting Message box window title
    msg.setWindowTitle("Attention")

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok)

    # start the app
    msg.exec_()


def show_question_messagebox(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)

    # setting message for Message Box
    msg.setText(text)

    # setting Message box window title
    msg.setWindowTitle("Question")

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    # start the app
    msg.exec_()


def show_critical_messagebox(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)

    # setting message for Message Box
    msg.setText(text)

    # setting Message box window title
    msg.setWindowTitle("Erreur")

    # declaring buttons on Message Box
    msg.setStandardButtons(QMessageBox.Ok)

    # start the app
    msg.exec_()
