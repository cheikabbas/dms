from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QScrollArea, QDialog, QApplication
from PyQt5.uic import loadUi

from messageBoxes import show_info_messagebox


class CustomButton(QPushButton):
    def __init__(self, label):
        super().__init__()
        self.setText(label)
        self.click_count = 0

    def nbclick_add(self):
        self.click_count += 1

    def nbclick_rem(self):
        self.click_count -= 1


class CustomPopup(QDialog):
    def __init__(self, button_labels, todo, affaire):
        super(CustomPopup, self).__init__()
        self.selected_var = None
        self.selected_vars = []
        self.setWindowTitle(todo)
        self.resize(350, 100)
        self.setLayout(QVBoxLayout())
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow the scroll area to resize its content
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Show vertical scroll bar as needed

        self.scroll_content = QWidget()
        self.scroll_content.setLayout(QVBoxLayout())

        self.ok_button = QPushButton("Valider")
        self.ok_button.setGeometry(50, 40, 100, 25)
        self.ok_button.clicked.connect(self.accept)

        self.create_buttons(button_labels)

        self.scroll_area.setWidget(self.scroll_content)
        self.layout().addWidget(self.scroll_area)
        self.layout().addWidget(self.ok_button)
        self.sheet = None
        self.affaire = affaire
        self.create_buttons(button_labels)
        self.exec_()

    def button_clicked(self):
        if self.affaire == "F":
            if self.sender().click_count == 0:
                self.sheet = self.sender().text()
                self.sender().setStyleSheet("background-color: red;")
                self.sender().nbclick_add()
            else:
                self.sheet = None
                self.sender().setStyleSheet("background-color: #f0f0f0;")
                self.sender().nbclick_rem()
        elif self.affaire == "V1":
            if self.sender().click_count == 0:
                self.selected_var = self.sender().text()
                self.sender().setStyleSheet("background-color: red;")
                self.sender().nbclick_add()
            else:
                self.selected_var = None
                self.sender().setStyleSheet("background-color: #f0f0f0;")
                self.sender().nbclick_rem()
        elif self.affaire == "VX":
            if self.sender().click_count == 0:
                var = self.sender().text()
                self.selected_vars.append(var)
                self.sender().setStyleSheet("background-color: red;")
                self.sender().nbclick_add()
            else:
                var = self.sender().text()
                self.selected_vars.remove(var)
                self.sender().setStyleSheet("background-color: #f0f0f0;")
                self.sender().nbclick_rem()

    def create_buttons(self, button_labels):
        for label in button_labels:
            button = CustomButton(label)
            button.clicked.connect(self.button_clicked)
            self.scroll_content.layout().addWidget(button)


class ResultText(QDialog):
    def __init__(self, resultats, title):
        super(ResultText, self).__init__()
        loadUi('ui/resultsText.ui', self)
        self.resultats = resultats
        self.res_title.setText(title)
        self.res.setPlainText(self.resultats)
        self.close_btn.clicked.connect(self.accept)
        self.copy_btn.clicked.connect(self.copy_text)
        self.exec_()

    def copy_text(self):
        text = self.res.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            show_info_messagebox("Resultats copiés dans le presse papier.")


class ResultData(QDialog):
    def __init__(self, df, title):
        super(ResultData, self).__init__()
        loadUi('ui/resultsData.ui', self)
        self.df = df
        self.title_lab.setText(title)
        self.close_btn.clicked.connect(self.accept)
        self.show_data()
        self.exec_()

    def show_data(self):
        model = QStandardItemModel(self.df.shape[0], self.df.shape[1])

        for row in range(self.df.shape[0]):
            for col in range(self.df.shape[1]):
                item = QStandardItem(str(self.df.iloc[row, col]))
                model.setItem(row, col, item)

        model.setHorizontalHeaderLabels(self.df.columns)
        self.table_view.setModel(model)
