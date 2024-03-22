import os

from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QMainWindow
from PyQt5.uic import loadUi

from custom_widgets import CustomPopup, ResultData
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
        self.outlier_btn.clicked.connect(self.outliers)
        self.duplicates_btn.clicked.connect(self.duplicate)
        self.data_table_btn.clicked.connect(self.show_data)
        self.export_data_btn.clicked.connect(self.exportdata)
        self.export_res_btn.clicked.connect(self.exportoutput)
        self.correct_na_btn.clicked.connect(self.corrections_na)
        self.label.setText(f'Nom du projet : {str(self.dms.globalPath).split("/")[-1]}')
        self.loaded_data = False
        self.disable_btn()

    def goto_home(self):
        self.parent().setCentralWidget(Home())

    def load_data(self):
        try:
            file, _ = QFileDialog.getOpenFileName(self, 'Sélectionner un fichier', self.dms.dataPath,
                                                  "Excel Files (*.xlsx)")
            if file is not None:
                sheets = self.dms.getsheetsnames(file)
                feuille = CustomPopup(sheets, "Choisir la feuille de données", "F")

                if feuille.sheet is not None:
                    self.dms.load_data(file, feuille.sheet)
                    self.loaded_data = True
                    self.disable_btn()
                    self.ope.setText(self.ope.toPlainText() + "\n-> Chargement de données")
                    show_info_messagebox(
                        f"Données importées avec succès. Il y a {self.dms.data.shape[0]} lignes et {self.dms.data.shape[1]} colonnes dans la base de données")
        except Exception:
            pass

    def missing(self):
        self.dms.missing_count()
        self.ope.setText(self.ope.toPlainText() + "\n-> Comptage de valeurs manquantes")

    def duplicate(self):
        variables = self.dms.data.columns
        choosedvars = CustomPopup(variables, "Choisir les variables", "VX")
        self.dms.duplicates_check(choosedvars.selected_vars)
        if len(choosedvars.selected_vars) > 0:
            self.ope.setText(
                self.ope.toPlainText() + f"\n-> Détection de doublons sur les variables {str(choosedvars.selected_vars)}")

    def outliers(self):
        variables = self.dms.data.columns
        var = CustomPopup(variables, "Choisir la variable", "V1")
        self.dms.outliers_check(var.selected_var)
        if var.selected_var is not None:
            self.ope.setText(
                self.ope.toPlainText() + f"\n-> Détection de valeurs aberrantes sur la variable {str(var.selected_var)}")

    def show_data(self):
        ResultData(self.dms.data, "Base de données")
        self.ope.setText(self.ope.toPlainText() + "\n-> Affichage de base de données")

    def exportdata(self):
        formats = ['CSV', 'Stata', 'SPSS']
        frmt = CustomPopup(formats, "Choisir le format d'exportation", "V1")
        self.dms.export_data(frmt.selected_var)
        if frmt.selected_var == "Stata":
            show_info_messagebox(
                f"Données exportées au format {frmt.selected_var} avec succès.\nCe format est supporté par Stata 15 et plus.")
            self.ope.setText(
                self.ope.toPlainText() + f"\n-> Exportation de base de données au format {frmt.selected_var}")
        if frmt.selected_var == "CSV" or frmt.selected_var == "SPSS":
            show_info_messagebox(f"Données exportées au format {frmt.selected_var} avec succès.")
            self.ope.setText(
                self.ope.toPlainText() + f"\n-> Exportation de base de données au format {frmt.selected_var}")

    def exportoutput(self):
        self.dms.export_output()

    def corrections_na(self):
        methods = ["Supprimer", "Remplacer"]
        variables = self.dms.data.columns
        method = CustomPopup(methods, "Choisir la méthode à appliquer", "V1")
        if method.selected_var == "Supprimer":
            var = CustomPopup(variables, "Choisir une variable", "V1")
            self.dms.na_correction(method.selected_var, var.selected_var)
            self.ope.setText(
                self.ope.toPlainText() + f"\n-> Suppression des valeurs manquantes pour la variable {var.selected_var}")

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
