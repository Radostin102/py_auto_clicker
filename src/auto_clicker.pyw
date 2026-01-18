import threading
import time
import os
import sys
import signal
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode, Key
import pystray
from PIL import Image
import tomllib

def load_config() -> dict:
    default_config: dict = {"click_interval": 0.05, "toggle_hotkey": "f4"}
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.toml")

        with open(config_path, "rb") as f:
            file_config = tomllib.load(f)
            default_config.update(file_config)

    except FileNotFoundError:
        print("Config file not found, using defaults.")
    except Exception as e:
        print(f"Error reading config: {e}, using defaults.")

    return default_config

class AutoClicker:
    """
    Handles the clicking logic in a separate thread to ensure
    non-blocking execution and precise timing.
    """
    def __init__(self, delay: float = 0.05, toggle_key: str = "f4") -> None:
        self.delay: float = delay

        try:
            self.toggle_key = getattr(Key, toggle_key.lower())
        except AttributeError:
            self.toggle_key = KeyCode(char=toggle_key)

        self.running: bool = False
        self.program_active: bool = True
        self.mouse: Controller = Controller()
        self.click_thread: threading.Thread = threading.Thread(target=self._click_loop, daemon=True)

    def start(self) -> None:
        self.click_thread.start()

    def _click_loop(self) -> None:
        while self.program_active:
            if self.running:
                self.mouse.click(Button.left, 1)
                time.sleep(self.delay)
            else:
                time.sleep(0.01)

    def toggle(self) -> None:
        self.running = not self.running

    def stop_program(self) -> None:
        self.program_active = False

class InputHandler:
    """ Manages global keyboard events to toggle the clicker. """
    def __init__(self, clicker_instance: AutoClicker) -> None:
        self.clicker: AutoClicker = clicker_instance
        self.listener: Listener = Listener(on_press=self._on_press)

    def start(self) -> None:
        self.listener.start()

    def stop(self) -> None:
        self.listener.stop()

    def _on_press(self, key) -> None:
        if key == self.clicker.toggle_key:
            self.clicker.toggle()

class SystemTrayApp:
    """ Manages the system tray icon and application lifecycle. """
    def __init__(self, clicker: AutoClicker, input_handler: InputHandler) -> None:
        self.clicker: AutoClicker = clicker
        self.input_handler: InputHandler = input_handler
        self.icon: pystray.Icon = pystray.Icon("AutoClicker", self._create_image(), "Auto Clicker")
        self.icon.menu: pystray.Menu = pystray.Menu(
            pystray.MenuItem("Exit", self._on_exit)
        )

    def _create_image(self) -> Image.Image:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon.png")

        try:
            return Image.open(icon_path)
        except FileNotFoundError:
            width: int = 64
            height: int = 64
            color: tuple[int, int, int] = (65, 105, 225)
            return Image.new("RGB", (width, height), color)

    def stop(self) -> None:
        self.clicker.stop_program()
        self.input_handler.stop()
        self.icon.stop()

    def _on_exit(self) -> None:
        self.stop()

    def run(self) -> None:
        self.clicker.start()
        self.input_handler.start()
        self.icon.run()

if __name__ == "__main__":
    config: dict = load_config()

    clicker_service: AutoClicker = AutoClicker(
        delay=config.get("click_interval", 0.05),
        toggle_key=config.get("toggle_hotkey", "f4")
    )
    input_service: InputHandler = InputHandler(clicker_service)
    app: SystemTrayApp = SystemTrayApp(clicker_service, input_service)

    def signal_handler(_sig, _frame) -> None:
        print("\nExiting")
        app.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    app.run()
