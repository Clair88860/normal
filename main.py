import cv2
import numpy as np
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.camera import Camera as CoreCamera
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission


class ScannerApp(App):

    def build(self):

        if platform == "android":
            request_permissions([Permission.CAMERA])

        self.layout = FloatLayout()

        # Kamera
        self.camera = CoreCamera(index=0, resolution=(1280, 720))
        self.camera.start()

        self.image = Image(size_hint=(1, 1))
        self.layout.add_widget(self.image)

        # Button
        self.capture_btn = Button(
            text="Scannen",
            size_hint=(1, 0.1),
            pos_hint={"x": 0, "y": 0}
        )
        self.capture_btn.bind(on_press=self.capture)
        self.layout.add_widget(self.capture_btn)

        Clock.schedule_interval(self.update, 1.0 / 30.0)

        return self.layout

    def update(self, dt):

        frame = self.camera.texture
        if not frame:
            return

        buf = frame.pixels
        w, h = frame.size
        img = np.frombuffer(buf, np.uint8).reshape(h, w, 4)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

        # Hochformat drehen
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        self.current_frame = img.copy()

        # Bild anzeigen
        flipped = cv2.flip(img, 0)
        tex = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt='bgr')
        tex.blit_buffer(flipped.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = tex

    def capture(self, instance):

        if not hasattr(self, "current_frame"):
            return

        cv2.imwrite("scan.jpg", self.current_frame)

        # Optional: Direkt das gespeicherte Bild anzeigen
        flipped = cv2.flip(self.current_frame, 0)
        tex = Texture.create(size=(self.current_frame.shape[1], self.current_frame.shape[0]), colorfmt='bgr')
        tex.blit_buffer(flipped.tobytes(), colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = tex


if __name__ == "__main__":
    ScannerApp().run()
