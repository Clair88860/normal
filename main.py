import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, PushMatrix, PopMatrix, Rotate
from kivy.metrics import dp
from kivy.core.window import Window

class CameraApp(App):
    def build(self):
        self.root_layout = FloatLayout()

        # ---------------- Kamera ----------------
        self.camera = Camera(play=True, resolution=(1280, 720))
        self.camera.size = (Window.width, Window.height)
        self.camera.pos = (0, 0)

        # ---------------- Kamera drehen ----------------
        with self.camera.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=-90, origin=self.camera.center)
        with self.camera.canvas.after:
            PopMatrix()

        self.root_layout.add_widget(self.camera)

        # ---------------- Aufnahme Button ----------------
        self.capture_btn = Button(
            size_hint=(None, None),
            size=(dp(80), dp(80)),
            pos_hint={"center_x": 0.5, "y": 0.05},
            background_color=(0,0,0,0)  # transparent, nur Grafik
        )
        self.capture_btn.bind(on_press=self.take_photo)

        # Runder Button zeichnen
        with self.capture_btn.canvas.before:
            Color(1, 1, 1, 1)
            self.circle = Ellipse(pos=self.capture_btn.pos, size=self.capture_btn.size)

        # Aktualisiere Kreis bei Position/Größe
        self.capture_btn.bind(pos=self.update_circle, size=self.update_circle)
        self.root_layout.add_widget(self.capture_btn)

        # Speicherort für Fotos
        self.photos_dir = os.path.join(self.user_data_dir, "photos")
        os.makedirs(self.photos_dir, exist_ok=True)

        # Bei Größenänderung Kamera skalieren
        Window.bind(on_resize=self.update_camera_size)

        return self.root_layout

    def update_camera_size(self, window, width, height):
        self.camera.size = (width, height)
        self.rot.origin = self.camera.center

    def update_circle(self, *args):
        self.circle.pos = self.capture_btn.pos
        self.circle.size = self.capture_btn.size

    def take_photo(self, instance):
        files = sorted([f for f in os.listdir(self.photos_dir) if f.endswith(".png")])
        next_num = len(files) + 1
        path = os.path.join(self.photos_dir, f"{next_num:04d}.png")
        self.camera.export_to_png(path)
        print(f"Foto gespeichert: {path}")

if __name__ == "__main__":
    CameraApp().run()
