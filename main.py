import socket
import threading
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

class ReceiverApp(App):
    def build(self):
        # Set the window size to a typical mobile screen size for testing
        Window.size = (360, 640)  # Width x Height in pixels for a mobile-like appearance

        # Create a FloatLayout as the root layout
        layout = FloatLayout()

        # Set the background color to white using canvas instructions
        with layout.canvas.before:
            Color(1, 1, 1, 1)  # Set color to white
            self.rect = Rectangle(size=layout.size, pos=layout.pos)

        layout.bind(size=self._update_rect, pos=self._update_rect)

        # Scrollable container for messages
        self.scroll_view = ScrollView(size_hint=(1, 0.85), pos_hint={'x': 0, 'top': 1})  # Scroll view at the top 85%
        self.message_container = GridLayout(cols=1, size_hint_y=None)
        self.message_container.bind(minimum_height=self.message_container.setter('height'))
        self.scroll_view.add_widget(self.message_container)

        # Button to start receiving messages
        self.start_button = Button(text='Start Receiving', size_hint=(1, None), height=50, pos_hint={'x': 0, 'y': 0})  # Button at the bottom
        self.start_button.bind(on_press=self.start_receiving)

        # Add the scroll view and button to the main layout
        layout.add_widget(self.scroll_view)
        layout.add_widget(self.start_button)

        return layout

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def add_message(self, message):
        # Add a new message to the display
        label = Label(text=message, size_hint_y=None, height=40, color=(0, 0, 0, 1))  # Set font color to black
        label.bind(size=self._update_label_size)  # Bind size change to update font size
        self.message_container.add_widget(label)

        # Automatically scroll to the bottom
        self.scroll_view.scroll_y = 0

    def _update_label_size(self, instance, size):
        # Adjust font size based on label size
        if size[0] > 0:  # Avoid division by zero
            instance.font_size = min(size[0] / 5, 11)  # Adjust font size relative to width (up to a maximum of 24)

    def start_receiving(self, instance):
        # Start the receiver thread to listen for UDP messages
        threading.Thread(target=self.receive_alert, daemon=True).start()
        self.start_button.disabled = True  # Disable the button after starting

    def receive_alert(self, host='', port=5000):
        # Set up socket to listen for incoming messages
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.bind((host, port))
                print(f"Listening for alerts on {host}:{port}...")
            except Exception as e:
                print(f"Error binding socket: {e}")
                return

            while True:
                try:
                    alert_message, _ = s.recvfrom(1024)  # Buffer size of 1024 bytes
                    # Format the message without sender IP and port
                    message = f"Alert: {alert_message.decode()}"
                    print(message)

                    # Use Clock to schedule the UI update on the main thread
                    Clock.schedule_once(lambda dt: self.add_message(message))
                except Exception as e:
                    print(f"Error receiving message: {e}")

if __name__ == '__main__':
    ReceiverApp().run()
