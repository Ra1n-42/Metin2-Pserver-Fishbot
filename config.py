import cv2
import numpy as np
import pyautogui
import time
import keyboard
import mss
import pydirectinput
import pygetwindow as gw
import ctypes
import logging
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

class Config:
    def __init__(self):
        self.PFAD_ZU_DEN_BILDERN = os.path.join(current_dir, "assets/").replace('\\', '/')

        # Beispielbilder des gelben Rechtecks und des halben Fisches in Originalgröße (Graustufen)
        self.TEMPLATE_YELLOW_GRAY = cv2.imread(self.PFAD_ZU_DEN_BILDERN + 'rechteck.png', cv2.IMREAD_GRAYSCALE)
        self.TEMPLATE_FISH_HALF_GRAY = cv2.imread(self.PFAD_ZU_DEN_BILDERN + 'fisch.png', cv2.IMREAD_GRAYSCALE)  # Halbes Fischbild nach rechts
        self.TEMPLATE_FISH_HALF_GRAY2 = cv2.imread(self.PFAD_ZU_DEN_BILDERN + 'fisch2.png', cv2.IMREAD_GRAYSCALE)  # Halbes Fischbild nach links
        self.TEMPLATE_MINIGAME = cv2.imread(self.PFAD_ZU_DEN_BILDERN + 'minigame_window.png', cv2.IMREAD_GRAYSCALE)  # Halbes Fischbild nach links

        # Fishing display
        # self.MINIGAME_X, self.MINIGAME_Y = 900, 398

        # Koordinaten und Dimensionen des Überwachungsbereichs
        self.X = 0 
        self.Y = 0

        self.CAPTURE_WIDTH = 311
        self.CAPTURE_HEIGHT = 16

        self.THRESHOLD = 0.95

        self.FANGZONE_CENTER = None

        # self.WINDOW_TITLE is the targeting window
        self.WINDOW_TITLE = "WindowName"
        
        self.NEW_TITLE = self.WINDOW_TITLE + "-fishing"

        self.MONITOR_INDEX = 1


    def get_window_screenshot(self):
        windows = gw.getWindowsWithTitle(self.NEW_TITLE)
        if windows:
            window = windows[0]
            window.activate()
            bbox = (window.left, window.top, window.right - window.left, window.bottom - window.top)
            screenshot = pyautogui.screenshot(region=bbox)
            return window, screenshot
        return None, None
    
    def find_image_in_screenshot(self, screenshot):
        template = self.TEMPLATE_MINIGAME
        template_w, template_h = template.shape[::-1]

        screenshot_np = np.array(screenshot)
        screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.87 # 87% Genauigkeit
        if max_val >= threshold:
            top_left = max_loc
            bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
            return top_left, bottom_right
        return None, None