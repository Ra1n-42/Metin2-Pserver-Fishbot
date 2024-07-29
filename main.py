
from config import *  # Importiere deine Konfigurationsvariablen

config = Config()

# Logging einrichten
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FishingBot:
    def __init__(self):
        self.fangzone_center = config.FANGZONE_CENTER
        self.monitor_index = config.MONITOR_INDEX
        self.screenshot = 0
        # Initialisiere den Monitor
        with mss.mss() as sct:
            if 0 <= self.monitor_index < len(sct.monitors):
                self.monitor = sct.monitors[self.monitor_index]
            else:
                raise ValueError(f"Monitor-Index {self.monitor_index} ist ungültig.")

        logging.info(f"Monitor ausgewählt: {self.monitor}")

    def is_fishing(self):
        x = config.X - 1
        y = config.Y
        r, g, b = pyautogui.pixel(x, y)
        return r == 0


    def check_exit_key(self):
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('q'):
            return True
        return False

    def set_window_title(self, window_title, new_title):
        window = gw.getWindowsWithTitle(window_title)
        if window:
            hwnd = window[0]._hWnd
            ctypes.windll.user32.SetWindowTextW(hwnd, new_title)
            logging.info(f"Fenstertitel geändert zu: {new_title}")
        else:
            logging.error(f"Fenster mit Titel '{window_title}' nicht gefunden.")

    def bring_window_to_front(self):
        window = gw.getWindowsWithTitle(config.NEW_TITLE)
        if window:
            window[0].activate()

    def capture_screen(self):
        # Region definieren
        region = {
            "top": config.Y,
            "left": config.X,
            "width": config.CAPTURE_WIDTH,
            "height": config.CAPTURE_HEIGHT
        }

        # Region für den Screenshot vorbereiten
        monitor = {
            "top": self.monitor["top"] + region["top"],
            "left": self.monitor["left"] + region["left"],
            "width": region["width"],
            "height": region["height"]
        }

        # logging.info(f"Screenshot-Region: {monitor}")

        # Screenshot des definierten Bereichs erstellen
        with mss.mss() as sct:
            return np.array(sct.grab(monitor))

    def process_image(self, image, template):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return max_val, max_loc

    def start_fishing(self):
        print("Angelbot läuft...")

        status = True
        
        while True:
            if self.check_exit_key():
                status = not status
                logging.info("Programm läuft jetzt weiter." if status else "Programm wurde pausiert.")
                time.sleep(2)
            
            if status:
                if not self.is_fishing():
                    self.bring_window_to_front()
                    pydirectinput.press('space')
                else:
                    cap = self.capture_screen()
                    # das hier drunter auskommentieren um bild vom bereich zu bekommen
                    # if not self.screenshot:
                        
                    #     cv2.imwrite('catch_screenshot.png', cap)
                    #     logging.info(f"Screenshot gespeichert unter: catch_screenshot.png")
                    #     self.screenshot = 1

                    max_val_yellow, max_loc_yellow = self.process_image(cap, config.TEMPLATE_YELLOW_GRAY)

                    if max_val_yellow >= config.THRESHOLD:
                        yellow_x, yellow_y = max_loc_yellow
                        self.fangzone_center = yellow_x + 20 - 2

                    max_val_fish, max_loc_fish = self.process_image(cap, config.TEMPLATE_FISH_HALF_GRAY)
                    max_val_fish2, max_loc_fish2 = self.process_image(cap, config.TEMPLATE_FISH_HALF_GRAY2)

                    max_val_fish = max(max_val_fish, max_val_fish2)
                    max_loc_fish = max_loc_fish if max_val_fish >= max_val_fish2 else max_loc_fish2

                    if max_val_fish >= config.THRESHOLD:
                        fish_x_position = max_loc_fish[0]
                        if self.fangzone_center and abs(fish_x_position - self.fangzone_center) <= 2:
                            self.bring_window_to_front()
                            pydirectinput.press('space')
                            time.sleep(1)


if __name__ == "__main__":
    bot = FishingBot()
    bot.set_window_title(config.WINDOW_TITLE, config.NEW_TITLE)
    print("Zum starten, Angel auswerfen...")
    while True:
        window, screenshot = config.get_window_screenshot()
        if screenshot:
            top_left, bottom_right = config.find_image_in_screenshot(screenshot)
            if top_left:
                desktop_x1 = window.left + top_left[0] + 1
                desktop_y1 = window.top + top_left[1] + 2
                config.X, config.Y = desktop_x1, desktop_y1
                break

    print(f"Minigame Fenster auf: ({config.X}, {config.Y}) gefunden.")
    bot.bring_window_to_front()
   
    bot.start_fishing()
    cv2.destroyAllWindows()
