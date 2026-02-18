import os
import math
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.utils import platform

# ---------------- Seite A: Kompass Widget ----------------
class CompassScreen(BoxLayout):
    def __init__(self, store: JsonStore, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.store = store

        # Hintergrund
        with self.canvas.before:
            Color(0, 0, 0.6, 1)  # Dunkelblau
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Label für Kompass
        self.label = Label(
            text="NORD: 0°",
            font_size="40sp",
            color=(1, 1, 1, 1),
            size_hint=(1, 0.5),
            halign="center",
            valign="middle"
        )
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.label)

        # Label nur wenn Arduino = Nein
        self.arduino_text = None
        if not (self.store.exists("arduino") and self.store.get("arduino")["value"]):
            self.arduino_text = Label(
                text="Hier werden später die Arduino Daten angezeigt.",
                font_size=24,
                size_hint=(1, 0.2)
            )
            self.add_widget(self.arduino_text)

        # Simulierte Winkelanzeige (später BLE/Arduino ersetzen)
        self.angle = 0
        Clock.schedule_interval(self.update_direction, 0.5)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def update_direction(self, dt):
        # 🔁 Simulation: Winkel erhöhen
        self.angle = (self.angle + 10) % 360
        dirs = ["N", "NO", "O", "SO", "S", "SW", "W", "NW"]
        direction = dirs[int((self.angle + 22.5) / 45) % 8]
        self.label.text = f"NORD: {self.angle}°\n{direction}"


# ---------------- Dashboard ----------------
class Dashboard(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore("settings.json")

        self.build_topbar()
        Clock.schedule_once(lambda dt: self.show_a(), 0.1)

    def build_topbar(self):
        self.topbar = BoxLayout(size_hint=(1, .08), pos_hint={"top": 1}, spacing=5, padding=5)
        for t, f in [("A", self.show_a), ("H", self.show_help), ("E", self.show_settings)]:
            b = Button(text=t, background_color=(0.15, 0.15, 0.15, 1), color=(1, 1, 1, 1))
            b.bind(on_press=f)
            self.topbar.add_widget(b)
        self.add_widget(self.topbar)

    def show_a(self, *args):
        self.clear_widgets()
        self.add_widget(self.topbar)
        compass = CompassScreen(store=self.store, size_hint=(1, 1))
        self.add_widget(compass)

    def show_help(self, *args):
        self.clear_widgets()
        self.add_widget(self.topbar)
        lbl = Label(text="Bei Fragen oder Problemen:\nE-Mail Support", font_size=20, pos_hint={"center_x": .5, "center_y": .5})
        self.add_widget(lbl)

    def show_settings(self, *args):
        self.clear_widgets()
        self.add_widget(self.topbar)
        layout = BoxLayout(orientation="vertical", padding=[20,120,20,20], spacing=20)
        layout.add_widget(Label(text="Einstellungen", font_size=32, size_hint_y=None, height=dp(60)))

        def create_toggle_row(text, key):
            row = BoxLayout(size_hint_y=None, height=dp(60))
            label = Label(text=text)
            btn_ja = Button(text="Ja", size_hint=(None,None), size=(dp(80), dp(45)))
            btn_nein = Button(text="Nein", size_hint=(None,None), size=(dp(80), dp(45)))
            value = self.store.get(key)["value"] if self.store.exists(key) else False
            def update(selected):
                if selected:
                    btn_ja.background_color = (0, 0.6, 0, 1)
                    btn_nein.background_color = (1,1,1,1)
                else:
                    btn_nein.background_color = (0,0.6,0,1)
                    btn_ja.background_color = (1,1,1,1)
            update(value)
            btn_ja.bind(on_press=lambda x: [self.store.put(key, value=True), update(True)])
            btn_nein.bind(on_press=lambda x: [self.store.put(key, value=False), update(False)])
            row.add_widget(label)
            row.add_widget(btn_ja)
            row.add_widget(btn_nein)
            return row

        layout.add_widget(create_toggle_row("Mit Arduino Daten", "arduino"))
        self.add_widget(layout)


# ---------------- Main App ----------------
class MainApp(App):
    def build(self):
        return Dashboard()


if __name__ == "__main__":
    MainApp().run()
