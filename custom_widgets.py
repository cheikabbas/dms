import seaborn as sns
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QScrollArea, QDialog, QApplication, QLineEdit, \
    QHBoxLayout, QLabel, QGraphicsView, QGraphicsScene, QMainWindow
from PyQt5.uic import loadUi
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from messageBoxes import show_info_messagebox, show_warning_messagebox


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
    def __init__(self, button_labels, todo, affaire, fillvalue=False):
        super(CustomPopup, self).__init__()
        self.selected_var = None
        self.selected_vars = []
        self.buttons = []
        self.valeur = None

        self.setWindowTitle(todo)
        self.resize(400, 100)

        self.setLayout(QVBoxLayout())
        self.layH = QHBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow the scroll area to resize its content
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Show vertical scroll bar as needed
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(QVBoxLayout())

        self.ok_button = QPushButton("Valider")
        self.ok_button.setGeometry(50, 40, 100, 25)
        self.ok_button.clicked.connect(self.popup_accept)

        self.spin_box = QLineEdit()
        self.spin_box_lab = QLabel("Valeur de remplacement")

        self.create_buttons(button_labels)

        self.scroll_area.setWidget(self.scroll_content)
        self.layH.addWidget(self.spin_box_lab)
        self.layH.addWidget(self.spin_box)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher")
        self.search_field.textChanged.connect(self.filter_buttons)

        self.layout().addWidget(self.search_field)
        self.layout().addWidget(self.scroll_area)
        if fillvalue:
            self.layout().addLayout(self.layH)
        self.layout().addWidget(self.ok_button)

        self.sheet = None
        self.affaire = affaire

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
            self.buttons.append(button)

    def filter_buttons(self, text):
        for button in self.buttons:
            if text.lower() in button.text().lower():
                button.setVisible(True)
            else:
                button.setVisible(False)

    def popup_accept(self):
        self.valeur = self.spin_box.text()
        self.accept()


class SampleView(QDialog):
    def __init__(self, maxval, chemin, sample_df=None):
        super(SampleView, self).__init__()
        loadUi('ui/sample01.ui', self)
        self.ssize = None
        self.valeur.setMinimum(1)
        self.valeur.setMaximum(maxval)
        self.sample_btn.clicked.connect(self.proceed)
        self.title = "Echantillon"
        self.sampled_df = sample_df
        self.show_btn.clicked.connect(self.show_sample)
        self.export_path = chemin

        self.exporter_btn.clicked.connect(self.export_sample)

        self.exec_()

    def proceed(self):
        self.ssize = self.valeur.value()
        self.accept()

    def show_sample(self):
        if self.sampled_df is not None:
            ResultData(self.sampled_df, self.title)
        else:
            show_warning_messagebox("Procéder d'abord à l'échantillonnage.")

    def export_sample(self):
        if self.sampled_df is not None:
            self.sampled_df.to_excel(self.export_path, index=False)
        else:
            show_warning_messagebox("Procéder d'abord à l'échantillonnage.")


class ResultText(QDialog):
    def __init__(self, resultats, title):
        super(ResultText, self).__init__()
        loadUi('ui/resultsText.ui', self)
        self.resultats = resultats
        self.res_title.setText(title)
        self.res.setHtml(str(self.resultats))
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


class Graphic(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a QGraphicsScene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Create a matplotlib figure and canvas
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        # Add the canvas to the scene
        self.scene.addWidget(self.canvas)

    def plot_data(self, x, data, typegraph=None):
        # Plot some data
        if typegraph == "Barres":
            sns.countplot(x=x, data=data)
            plt.title(f"Diagramme en barres de {x}")
            plt.ylabel("Nombre")
            plt.show()
        self.canvas.draw()


class GraphShow(QMainWindow):
    def __init__(self, x, data, typegraph):
        super(GraphShow, self).__init__()

        self.x = x
        self.data = data
        self.typegraph = typegraph

        self.setWindowTitle("Graphique")
        self.setGeometry(100, 100, 800, 600)

        # Create a layout
        layout = QVBoxLayout()

        # Create a MatplotlibView widget
        self.matplotlib_view = Graphic()

        # Add the MatplotlibView widget to the layout
        layout.addWidget(self.matplotlib_view)

        # Create a QWidget for the layout
        widget = QWidget()
        widget.setLayout(layout)

        # Set the central widget of the QMainWindow
        self.setCentralWidget(widget)

        # Plot some data
        self.matplotlib_view.plot_data(x=self.x, data=self.data, typegraph=self.typegraph)
