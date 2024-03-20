from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QScrollArea, QDialog
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView


class CustomButton(QPushButton):
    def __init__(self, label):
        super().__init__()
        self.setText(label)
        self.click_count = 0

    def nbclick_add(self):
        self.click_count += 1

    def nbclick_rem(self):
        self.click_count -= 1


class ChooseVar(Screen):

    def __init__(self, items, text="", **kwargs):
        super(ChooseVar, self).__init__(**kwargs)
        self.varname = ""
        self.varnames = []
        scroll_view = ScrollView()

        self.my_box1 = BoxLayout(orientation="vertical", spacing=50)
        self.my_box1.bind(minimum_height=self.my_box1.setter('height'))
        my_grid1 = GridLayout(cols=1, pos_hint={'center_x': 0.5}, size_hint_y=None)
        my_grid1.bind(minimum_height=my_grid1.setter('height'))
        my_label = Label(text=text, font_size='24dp', color="lime")
        close_button = Button(text='Fermer', size_hint=(None, None), size=(200, 50), pos_hint={'center_x': 0.5})
        close_button.bind(on_release=self.close_app)
        for item in items:
            btn = CustomButton(text=str(item), size_hint=(None, None), size=(1200, 50), color='lime')
            btn.bind(on_release=lambda btn_item: self.select_varnames(btn_item, varname=self.varname,
                                                                      varnames=self.varnames))
            my_grid1.add_widget(btn)
        self.my_box1.add_widget(my_label)
        scroll_view.add_widget(my_grid1)
        self.my_box1.add_widget(scroll_view)
        self.my_box1.add_widget(close_button)

    def close_app(self, instance):
        # This function is called when the close button is pressed
        App.get_running_app().stop()

    def select_varnames(self, btn, varname, varnames, one=False):
        if one is False:
            if btn.click_count == 0:
                varnames.append(str(btn.text))
                btn.color = 'red'
                btn.nbclick_add()
            else:
                varnames.remove(str(btn.text))
                btn.color = 'lime'
                btn.nbclick_rem()
        if one is True:
            if btn.click_count == 0:
                varname = str(btn.text)
                btn.color = 'red'
                btn.nbclick_add()
            else:
                varname = str(btn.text)
                btn.color = 'lime'
                btn.nbclick_rem()


class CustomPopup(QDialog):
    def __init__(self, button_labels, todo, affaire):
        super(CustomPopup, self).__init__()
        self.selected_var = None
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
        # elif self.affaire == "V1":
        #     self.selected_var = self.sender().text()
        # else:
        #     var = self.sender().text()
        #     self.selected_vars.append(var)

    def create_buttons(self, button_labels):
        for label in button_labels:
            button = CustomButton(label)
            button.clicked.connect(self.button_clicked)
            self.scroll_content.layout().addWidget(button)
