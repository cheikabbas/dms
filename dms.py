import shutil

import pandas as pd
import os
import openpyxl
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from openpyxl.utils.dataframe import dataframe_to_rows
import datetime

from messageBoxes import show_critical_messagebox, show_info_messagebox


class Dms:
    """Cette classe a des fonctions pour vérifier la qualité des données lors d'une collecte de données"""

    def __init__(self):
        self.duplicates = None
        self.na = None
        self.globalPath = None
        self.dataPath = None
        self.outputPath = None
        self.correctionsPath = None
        self.filesList = []
        self.data = None
        self.outliers = []
        self.workbook = openpyxl.Workbook()
        self.operations = ["#################### VERIFICATIONS A FAIRE ####################"]

    # Create new project
    def create_project(self, chemin, nom_projet, data):
        """Crée un projet de suivi de la qualité des données"""
        self.globalPath = os.path.join(chemin, nom_projet)
        if not os.path.exists(self.globalPath):
            os.makedirs(self.globalPath)
            file_config = os.path.join(self.globalPath, "config.dms")
            with open(file_config, "x") as f:
                f.write(f"Created on {get_datetime()}\n")
                f.write(self.globalPath)
            for i in ["data", "output", "corrections"]:
                os.makedirs(os.path.join(self.globalPath, i))
            self.dataPath = os.path.join(self.globalPath, "data")
            self.outputPath = os.path.join(self.globalPath, "output")
            self.correctionsPath = os.path.join(self.globalPath, "corrections")

            try:
                shutil.copy(data, self.dataPath)
            except IOError as e:
                show_critical_messagebox("Impossible de copier le fichier de données. " + e)

            return "Projet créé avec succès! Copier le fichier le données dans le dossier 'data' créé pour continuer."
        return "Dossier existe déjà."

    # Open existing project
    def open_project(self, chemin):
        self.globalPath = chemin
        self.dataPath = os.path.join(self.globalPath, "data")
        self.outputPath = os.path.join(self.globalPath, "output")
        self.correctionsPath = os.path.join(self.globalPath, "corrections")

    # Get Sheets names of Excel file
    @staticmethod
    def getsheetsnames(file):
        workbook = openpyxl.load_workbook(file)
        sheet_names = workbook.sheetnames
        return sheet_names

    # Load data file
    def load_data(self, fichier, sheet_name):
        self.data = pd.read_excel(fichier, sheet_name=sheet_name)

    def missing_count(self):
        nb_na = self.data.isnull().sum()
        pct_na = round(self.data.isna().mean() * 100, 2)
        self.na = pd.DataFrame({"Nombre de valeurs manquantes": nb_na, "Pourcentage de valeurs manquantes": pct_na})
        five_pct = self.na[pct_na > 0.0].index.tolist()
        self.operations.append("### VARIABLES CONTENANT DES VALEURS MANQUANTES ###")
        for name in five_pct:
            op = f"-> [{name}]"
            self.operations.append(op)
        show_info_messagebox("Le comptage de valeurs manquantes a été effetué avec succès.")

    def duplicates_check(self, varnames, popup):
        if len(varnames) > 0:
            self.duplicates = self.data[self.data.duplicated(subset=varnames, keep=False)]
            dups = self.duplicates.index.tolist()
            self.operations.append("### DOUBLONS ###")
            for name in dups:
                op = f"-> La ligne N°{name + 1} est un doublon si on considère la(les) variable(s) {varnames}."
                self.operations.append(op)
        else:
            show_message("Sélectionner au moins une variable")
        popup.dismiss()

    def outliers_check(self, varname, popup):
        if varname is not None:
            q1 = self.data[varname].quantile(0.25)
            q3 = self.data[varname].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            self.outliers.append(self.data[(self.data[varname] < lower_bound) | (self.data[varname] > upper_bound)])
            outliers = pd.concat(self.outliers).index.tolist()
            self.operations.append("### VALEURS ABBERANTES ###")
            for name in outliers:
                op = f"-> La ligne N°{name + 1} a une valeur abberante pour la variable [{varname}]."
                self.operations.append(op)
            popup.dismiss()
        else:
            show_message("Sélectionner une variable")

    def export_output(self):
        if (self.na is None) and (self.duplicates is None) and (len(self.outliers) == 0):
            show_message("Aucun résultat à exporter")
        else:
            self.workbook.create_sheet("Valeurs manquantes")
            worksheet = self.workbook["Valeurs manquantes"]
            if self.na is not None:
                for row in dataframe_to_rows(self.na):
                    worksheet.append(row)
            worksheet.delete_rows(2)

            self.workbook.create_sheet("Doublons")
            worksheet = self.workbook["Doublons"]
            if self.duplicates is not None:
                for row in dataframe_to_rows(self.duplicates):
                    worksheet.append(row)
            worksheet.delete_rows(2)

            self.workbook.create_sheet("Valeurs abbérantes")
            worksheet = self.workbook["Valeurs abbérantes"]
            if len(self.outliers) > 0:
                for row in dataframe_to_rows(pd.concat(self.outliers), header=True):
                    worksheet.append(row)
            worksheet.delete_rows(2)

            self.write_corrections()
            try:
                date_time = get_datetime()
                self.workbook.save(str(self.outputPath) + '/' + 'output-' + date_time + '.xlsx')
                show_message("Exportation réussie!!")
            except:
                show_message("Fermer le fichier output avant de recommencer")

    def reinit(self):
        self.na = None
        self.duplicates = None
        for sheet_name in self.workbook.sheetnames:
            sheet = self.workbook[sheet_name]
            self.workbook.remove(sheet)

    def write_corrections(self):
        date_time = get_datetime()
        correction_file = str(self.correctionsPath) + '/' + "corrections-" + date_time + ".txt"
        if os.path.exists(correction_file):
            with open(correction_file, 'a') as file:
                for text in self.operations:
                    file.write(text)
                    file.write('\n')
        else:
            with open(correction_file, 'w') as file:
                for text in self.operations:
                    file.write(text)
                    file.write('\n')


def show_message(msg):
    # Create a Popup with a Label and an "OK" button
    content = BoxLayout(orientation='vertical', spacing=10)
    message_label = Label(text=msg)
    ok_button = Button(text="OK")

    # Create the Popup widget
    popup = Popup(title="Message", content=content, size_hint=(None, None), size=(1000, 200))

    # Bind the "OK" button to close the Popup
    ok_button.bind(on_release=popup.dismiss)

    # Add the Label and Button to the Popup's content
    content.add_widget(message_label)
    content.add_widget(ok_button)

    # Open the Popup
    popup.open()


def get_datetime():
    """Retourne la date et l'heure pour nommer les fichiers"""
    current_datetime = datetime.datetime.now()
    # Format the new datetime
    formatted_datetime = current_datetime.strftime("%d%m%Y-%H%M%S")
    # Return the formatted datetime
    return formatted_datetime
