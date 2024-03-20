import os
import sys

from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QMainWindow
from PyQt5.uic import loadUi

from custom_widgets import CustomPopup
from dms import Dms
from messageBoxes import show_info_messagebox, show_warning_messagebox


class Home(QWidget):
    def __init__(self):
        super(Home, self).__init__()
        self.projectopened = None
        loadUi("ui/home.ui", self)
        self.dms = Dms()
        self.newproject.clicked.connect(self.goto_newproject)
        self.openproject.clicked.connect(self.open_project)

    def open_project(self):
        try:
            directory = QFileDialog.getExistingDirectory(self, 'Sélectionner le projet',
                                                         'C:/Users/ChargéMeal-RRM.bf/Desktop')
            if os.path.isfile(os.path.join(directory, 'config.dms')):
                self.dms.open_project(directory)
            self.goto_projectopened()
        except Exception as e:
            print(e)

    def goto_projectopened(self):
        if os.path.isfile(os.path.join(str(self.dms.globalPath), 'config.dms')):
            self.projectopened = ProjectOpened(self.dms)
            self.parent().setCentralWidget(self.projectopened)

    def goto_newproject(self):
        self.parent().setCentralWidget(NewProject())


class NewProject(QWidget):
    def __init__(self):
        super(NewProject, self).__init__()
        self.projectopened = None
        self.dms = Dms()
        self.raw_data_file = None
        self.globalPathDir = None
        loadUi('ui/newproject.ui', self)
        self.cancel.clicked.connect(self.goto_home)
        self.repertoire.clicked.connect(self.directory_url)
        self.browse_data.clicked.connect(self.data_url)
        self.createproject.clicked.connect(self.create_project)

    def directory_url(self):
        directory = QFileDialog.getExistingDirectory(self, 'Sélectionner un dossier', 'C:/Users/')
        self.globalPathDir = directory
        self.dir_url.setText(directory)

    def data_url(self):
        try:
            file, _ = QFileDialog.getOpenFileName(self, 'Sélectionner un fichier', 'C:/Users/')
            self.raw_data_file = file
            self.dta_url.setText(file)
        except Exception as e:
            print(e)

    def create_project(self):
        if self.globalPathDir is not None and self.projectname.text() is not None and self.raw_data_file is not None:
            self.dms.create_project(self.globalPathDir, self.projectname.text(), self.raw_data_file)
            show_info_messagebox("Projet créé avec succès")
            self.projectname.setText("")
            self.dir_url.setText("")
            self.dta_url.setText("")
            self.goto_projectopened()
        else:
            show_warning_messagebox("Remplir tous les champs correctement")

    def goto_projectopened(self):
        self.projectopened = ProjectOpened(self.dms)
        self.parent().setCentralWidget(self.projectopened)

    def goto_home(self):
        self.parent().setCentralWidget(Home())


class ProjectOpened(QWidget):
    def __init__(self, dms: Dms):
        super(ProjectOpened, self).__init__()
        loadUi('ui/projectopened.ui', self)
        self.dms = dms
        self.close.clicked.connect(self.goto_home)
        self.quitter.clicked.connect(QApplication.instance().quit)
        self.loading_data.clicked.connect(self.load_data)
        self.missing_btn.clicked.connect(self.missing)
        self.duplicates_btn.clicked.connect(self.duplicate)
        self.label.setText(f'Nom du projet : {str(self.dms.globalPath).split("/")[-1]}')
        self.loaded_data = False
        self.disable_btn()

    def goto_home(self):
        self.parent().setCentralWidget(Home())

    def load_data(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Sélectionner un fichier', self.dms.dataPath,
                                              "Excel Files (*.xlsx)")
        sheets = self.dms.getsheetsnames(file)
        feuille = CustomPopup(sheets, "Choisir la feuille de données", "F")

        if feuille.sheet is not None:
            self.dms.load_data(file, feuille.sheet)
            self.loaded_data = True
            self.disable_btn()
            self.ope.setText(self.ope.toPlainText() + "\n-> Chargement de données")
            show_info_messagebox(
                f"Données importées avec succès. Il y a {self.dms.data.shape[0]} lignes et {self.dms.data.shape[1]} colonnes dans la base de données")

    def missing(self):
        self.dms.missing_count()
        self.ope.setText(self.ope.toPlainText() + "\n-> Comptage de valeurs manquantes")

    def duplicate(self):
        variables = self.dms.data.columns

    def disable_btn(self):
        self.duplicates_btn.setEnabled(self.loaded_data)
        self.outlier_btn.setEnabled(self.loaded_data)
        self.correct_na_btn.setEnabled(self.loaded_data)
        # self.loading_data.setEnabled(self.loaded_data)
        self.export_data_btn.setEnabled(self.loaded_data)
        self.export_res_btn.setEnabled(self.loaded_data)
        self.sampling_btn.setEnabled(self.loaded_data)
        self.missing_btn.setEnabled(self.loaded_data)
        self.data_table_btn.setEnabled(self.loaded_data)
        self.stat_test_btn.setEnabled(self.loaded_data)
        self.datavis_btn.setEnabled(self.loaded_data)
        self.desc_analysis_btn.setEnabled(self.loaded_data)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.page1 = Home()
        self.setCentralWidget(self.page1)


class Popup():
    pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(930, 600)
    window.show()
    sys.exit(app.exec_())