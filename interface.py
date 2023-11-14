import os

import kivy
from kivy.app import App
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from dms import Dms
from custom_widgets import CustomButton, ChooseVar, ChVar

kivy.require('2.1.1')

Builder.load_file('main.kv')


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


class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        my_box1 = BoxLayout(orientation='vertical')

        dms_label = Label(text="OUTIL DE CONTROLE QUALITE DE DONNEES", font_size='24dp', color="lime")

        new_project = Button(text="Créer un project", size_hint_y=None)
        new_project.bind(on_press=self.newproject)
        open_project = Button(text="Ouvrir un projet", size_hint_y=None)
        open_project.bind(on_press=self.openproject)

        my_box2 = BoxLayout()
        my_box2.add_widget(new_project)
        my_box2.add_widget(open_project)

        my_box1.add_widget(dms_label)
        my_box1.add_widget(my_box2)
        self.add_widget(my_box1)

    def newproject(self, *args):
        self.manager.current = 'newproject'

    def openproject(self, *args):
        self.manager.current = 'openproject'


class NewProject(Screen):

    def __init__(self, projectopened, **kwargs):
        super(NewProject, self).__init__(**kwargs)

        self.projectOpened = projectopened
        self.globalPath = None
        self.dataPath = None
        self.outputPath = None
        self.correctionsPath = None
        self.chemin = None

        my_box1 = BoxLayout(orientation='vertical', spacing=50)
        my_grid = GridLayout(cols=2, size_hint=(None, None), width=800, height=20, pos_hint={'center_x': 0.5})

        nomProjetLabel = Label(text="Nom du projet:", size_hint=(1, None), font_size='20dp', color='lime', height=50)
        self.nomProjetInput = TextInput(multiline=False, size_hint=(1, None), font_size='20dp',
                                        pos_hint={'center_x': 0.5}, height=50)

        self.file_choose = FileChooserIconView(path='/', filters=['*.txt', '*.xlsx'])

        my_grid.add_widget(nomProjetLabel)
        my_grid.add_widget(self.nomProjetInput)

        my_label1 = Label(text="Créer un nouveau projet", font_size='24dp', color='lime', size_hint=(None, None),
                          pos_hint={'center_x': 0.5})

        button_create = Button(text="Créer", size_hint_y=None)
        button_create.bind(on_press=lambda fun: self.createproject())
        button_back = Button(text="Retour", size_hint_y=None)
        button_back.bind(on_press=self.back)

        self.home_button = Button(text="Accueil", size_hint=(None, None), width=200, height=50, pos_hint={'center_x': 0.5}, color='lime')
        self.home_button.bind(on_release=lambda fun: self.back())

        my_box2 = BoxLayout()

        my_box1.add_widget(my_label1)
        my_box1.add_widget(self.file_choose)
        my_box1.add_widget(self.home_button)
        my_box1.add_widget(my_grid)
        my_box2.add_widget(button_create)
        my_box2.add_widget(button_back)
        my_box1.add_widget(my_box2)
        self.add_widget(my_box1)

    def create_project(self, chemin, nom_projet):
        """Crée un projet de suivi de la qualité des données"""
        self.globalPath = os.path.join(chemin, nom_projet)
        if not os.path.exists(self.globalPath):
            os.makedirs(self.globalPath)
            file_config = os.path.join(self.globalPath, "config.txt")
            with open(file_config, "x") as f:
                f.write("")
            for i in ["data", "output", "corrections"]:
                os.makedirs(os.path.join(self.globalPath, i))
            self.dataPath = os.path.join(self.globalPath, "data")
            self.outputPath = os.path.join(self.globalPath, "output")
            self.correctionsPath = os.path.join(self.globalPath, "corrections")
            return "Projet créé avec succès! Copier le fichier le données dans le dossier 'data' créé pour continuer."
        return "Dossier existe déjà."

    def get_selection(self, direct, proj):
        try:
            self.chemin = str(os.path.join(direct, proj))
        except:
            pass

    def createproject(self, *args):
        selected_dir = self.file_choose.path
        if selected_dir:
            project_name = str(self.nomProjetInput.text)
            self.get_selection(direct=selected_dir, proj=project_name)
            msg = self.create_project(chemin=selected_dir, nom_projet=project_name)
            show_message(msg)
            self.nomProjetInput.text = ""
        else:
            show_message("Sélectionner un dossier")
        self.projectOpened.updatelabel(self.chemin)
        self.manager.current = 'projectopened'

    def back(self, *args):
        self.manager.current = 'home'


class OpenProject(Screen):
    def __init__(self, projectopened, **kwargs):
        super(OpenProject, self).__init__(**kwargs)
        self.projectOpened = projectopened

        self.chemin = None
        self.globalPath = None
        self.dataPath = None
        self.outputPath = None
        self.correctionsPath = None

        my_box1 = BoxLayout(orientation='vertical')

        self.my_label1 = Label(text="Ouvrir le dossier du projet",
                               font_size='24dp', color='lime')

        self.file_choose = FileChooserIconView(path='/', filters=['*.txt', '*.xlsx'])

        self.file_config = False

        button_create = Button(text="Ouvrir", size_hint_y=None)
        button_create.bind(on_press=self.openproject)
        button_back = Button(text="Retour", size_hint_y=None)
        button_back.bind(on_press=self.back)

        my_box2 = BoxLayout()

        my_box1.add_widget(self.my_label1)
        my_box1.add_widget(self.file_choose)
        my_box2.add_widget(button_create)
        my_box2.add_widget(button_back)
        my_box1.add_widget(my_box2)
        self.add_widget(my_box1)

    def open_project(self, chemin):
        self.globalPath = chemin
        self.dataPath = os.path.join(self.globalPath, "data")
        self.outputPath = os.path.join(self.globalPath, "output")
        self.correctionsPath = os.path.join(self.globalPath, "corrections")

    def openproject(self, *args):
        if os.path.isfile(os.path.join(self.file_choose.path, 'config.txt')):
            self.get_selection()
            self.manager.current = 'projectopened'
            self.open_project(self.chemin)
            self.projectOpened.updatelabel(self.chemin)
        else:
            show_message("Le fichier config.txt n'est pas dans ce dossier. Veuillez ouvrir le bon dossier.")

    def back(self, *args):
        self.manager.current = 'home'

    def get_selection(self):
        try:
            self.chemin = str(self.file_choose.path)
        except:
            pass


class ProjectOpened(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.varname = None
        self.my_grid = None
        self.my_box1 = None
        self.my_label1 = None
        self.button_reinit = None
        self.selected_var = None
        self.varnames = []
        self.button_export = None
        self.dms = Dms()
        self.file = None

    def updatelabel(self, text):
        self.ids.label1.text = f'Projet ouvert : {text}'
        self.ids.filechooser.path = str(text) + '/' + 'data'

    def opendata(self):
        self.dms.open_project(os.path.dirname(self.ids.filechooser.path))

        self.file = str(self.ids.filechooser.selection[0])

        items = self.dms.getsheetsnames(self.file)

        popup_layout = BoxLayout(orientation='vertical', spacing=10)

        # Create a Label to display the selected item
        selected_item_label = Label(text="Sélectionner la feuille")

        dropdown = DropDown(pos_hint={'center_x': 0.5}, size_hint=(None, None), size=(200, 100))

        # Create the popup
        popup = Popup(title=self.file.split("\\")[-1], content=popup_layout, size_hint=(None, None), size=(500, 300))

        for item in items:
            btn = Button(text=str(item), size_hint=(None, None), size=(195, 50), color='lime')
            btn.bind(on_release=lambda btn_item: self.select_dropdown_item(btn_item, popup))
            dropdown.add_widget(btn)

        # Add the selected item label, open dropdown button, and dropdown to the popup layout
        popup_layout.add_widget(selected_item_label)
        popup_layout.add_widget(dropdown)

        # Open the popup
        popup.open()

    def select_dropdown_item(self, btn, popup):
        selected_item = btn.text
        self.dms.load_data(fichier=self.file, sheet_name=selected_item)
        popup.dismiss()
        show_message(f"La base de données contient {self.dms.data.shape[0]} lignes et {self.dms.data.shape[1]} colonnes.")
        self.ids.layout1.clear_widgets()
        self.populate_screen(selected_item)

    def populate_screen(self, sheet):
        """Remets d'autres widgets dans layout1 après avoir effacer"""
        self.my_box1 = BoxLayout(orientation='vertical', spacing=10)
        file = self.file.split('\\')[-1]
        self.my_label1 = Label(text=f"{file} -- {sheet}", font_size='24dp', color='lime')
        self.my_grid = GridLayout(rows=3, size_hint=(None, None), width=800, height=400, pos_hint={'center_x': 0.5})

        # Missing values check
        missing = Button(text="Valeurs manquantes", size_hint_y=None, height=50, color='lime')
        missing.bind(on_release=lambda btn_item: self.missings(instance=missing))
        self.my_grid.add_widget(missing)

        # Duplicates values check
        duplicates = Button(text="Doublons", size_hint_y=None, height=50, color='lime')
        duplicates.bind(on_release=lambda btn_item: self.duplicated(instance=duplicates))
        self.my_grid.add_widget(duplicates)

        # Outliers
        outliers = Button(text="Valeurs abbérantes", size_hint_y=None, height=50, color='lime')
        outliers.bind(on_release=lambda btn_item: self.outliers(instance=outliers))
        self.my_grid.add_widget(outliers)

        # Home button
        self.home_button = Button(text="Accueil", size_hint=(None, None), width=200, height=50, pos_hint={'center_x': 0.5}, color='lime')
        self.home_button.bind(on_release=lambda fun: self.back())

        # Export button
        self.button_export = Button(text="Exporter les resultats", size_hint_y=None, height=50, color='lime')
        self.button_export.bind(on_release=lambda btn_item: self.export())

        # Renit button
        self.button_reinit = Button(text="Réinitialiser tout", size_hint_y=None, height=50, color='lime')
        self.button_reinit.bind(on_release=lambda btn_item: self.reinit())

        my_box = BoxLayout(spacing=10)
        my_box.add_widget(self.button_export)
        my_box.add_widget(self.button_reinit)

        self.my_box1.add_widget(self.my_label1)
        self.my_box1.add_widget(self.my_grid)
        self.my_box1.add_widget(self.home_button)
        self.my_box1.add_widget(my_box)
        self.add_widget(self.my_box1)

    def back(self):
        self.manager.current = 'home'

    def missings(self, instance):
        self.dms.missing_count()
        instance.color = 'red'

    def duplicated(self, instance):
        items = self.dms.data.columns
        popup_layout = BoxLayout(orientation='vertical', spacing=10)
        self.selected_var = Label(text="")
        dropdown = DropDown(pos_hint={'center_x': 0.5}, size_hint=(None, None), size=(200, 100))

        # Create the popup
        popup = Popup(title="Sélectionner les variables", content=popup_layout, size_hint=(None, None), size=(500, 300))

        launch_button = Button(text="Ok", size_hint_y=None, height=50, color='lime')
        launch_button.bind(on_release=lambda btn_item: self.dms.duplicates_check(self.varnames, popup))

        close_button = Button(text="Fermer", size_hint_y=None, height=50, color='lime')
        close_button.bind(on_release=popup.dismiss)

        for item in items:
            btn = CustomButton(text=str(item), size_hint=(None, None), size=(195, 50), color='lime')
            btn.bind(on_release=lambda btn_item: self.select_varnames(btn_item))
            dropdown.add_widget(btn)

        popup_layout2 = BoxLayout(spacing=10)
        popup_layout2.add_widget(launch_button)
        popup_layout2.add_widget(close_button)
        # Add the selected item label, open dropdown button, and dropdown to the popup layout
        popup_layout.add_widget(self.selected_var)
        popup_layout.add_widget(dropdown)
        popup_layout.add_widget(popup_layout2)
        #
        popup.open()
        # ChVar(items, text="Choisir des variables").run()
        instance.color = 'red'

    def outliers(self, instance):
        items = self.dms.data.select_dtypes(include=[int, float]).columns.tolist()
        popup_layout = BoxLayout(orientation='vertical', spacing=10)
        self.selected_var = Label(text="")
        dropdown = DropDown(pos_hint={'center_x': 0.5}, size_hint=(None, None), size=(200, 100))

        # Create the popup
        popup = Popup(title="Sélectionner une variable", content=popup_layout, size_hint=(None, None), size=(500, 300))

        launch_button = Button(text="Ok", size_hint_y=None, height=50, color='lime')
        launch_button.bind(on_release=lambda btn_item: self.dms.outliers_check(self.varname, popup))

        close_button = Button(text="Fermer", size_hint_y=None, height=50, color='lime')
        close_button.bind(on_release=popup.dismiss)

        for item in items:
            btn = CustomButton(text=str(item), size_hint=(None, None), size=(195, 50), color='lime')
            btn.bind(on_release=lambda btn_item: self.select_varnames(btn_item, one=True))
            dropdown.add_widget(btn)

        popup_layout2 = BoxLayout(spacing=10)
        popup_layout2.add_widget(launch_button)
        popup_layout2.add_widget(close_button)
        # Add the selected item label, open dropdown button, and dropdown to the popup layout
        popup_layout.add_widget(self.selected_var)
        popup_layout.add_widget(dropdown)
        popup_layout.add_widget(popup_layout2)

        popup.open()
        if self.varname != "":
            instance.color = 'red'

    def select_varnames(self, btn, one=False):
        if one is False:
            if btn.click_count == 0:
                self.varnames.append(str(btn.text))
                btn.color = 'red'
                btn.nbclick_add()
            else:
                self.varnames.remove(str(btn.text))
                btn.color = 'lime'
                btn.nbclick_rem()
        if one is True:
            if btn.click_count == 0:
                self.varname = str(btn.text)
                btn.color = 'red'
                btn.nbclick_add()
            else:
                self.varname = str(btn.text)
                btn.color = 'lime'
                btn.nbclick_rem()

    def export(self):
        self.dms.export_output()

    def reinit(self):
        self.dms.reinit()
        self.varnames = []
        for child in reversed(self.my_grid.children):
            child.color = "lime"


class TestApp(App):

    def build(self):
        self.icon = 'images/icon.png'
        my_screenmanager = ScreenManager()
        home = HomeScreen(name='home')
        projectOpened = ProjectOpened(name="projectopened")
        newProject = NewProject(name='newproject', projectopened=projectOpened)
        openProject = OpenProject(name='openproject', projectopened=projectOpened)
        my_screenmanager.add_widget(home)
        my_screenmanager.add_widget(newProject)
        my_screenmanager.add_widget(openProject)
        my_screenmanager.add_widget(projectOpened)
        return my_screenmanager
