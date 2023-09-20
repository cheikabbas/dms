from kivy.uix.button import Button


class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.click_count = 0

    def nbclick_add(self):
        self.click_count += 1

    def nbclick_rem(self):
        self.click_count -= 1
