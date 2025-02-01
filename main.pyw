import sys
import os
import pgzero
import pygame
import time
import json
import cv2
from screeninfo import get_monitors
import psutil
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import pygetwindow as gw
import ctypes
import subprocess

# Importing custom libraries
from classes import *
from functions import *


# Lower the process priority
p = psutil.Process(os.getpid())
p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)  


# Contains every app parameter affected by the config.json file
def config_changes():
    global config, video_path, cap, FPS
    for i in range(20):
        try:
            # Reading the video
            video_path = f'videos/{config["current"]}.mp4'
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("This video does not exist")

            # Setting the frame rate
            FPS = config["fps"]
            if FPS == 0:
                raise ValueError("FPS can not be equal to 0")

            break
        except:
            # Reading the config backup
            with open("config_backup.json", "r") as f:
                config = json.load(f)
            # Rewriting the config.json file
            with open("config.json", "w") as f:
                json.dump(config, f)


# Making an icon in the hidden icons menu
system_tray_started = False

def create_image():
    """Create an icon for the system tray."""
    image = Image.new('RGB', (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill=(0, 0, 255))
    return image

def setup_system_tray():
    """Set up the system tray icon and menu."""
    def on_exit(icon, item):
        icon.stop()
        # Stop the game when the tray icon menu is exited
        windows = gw.getWindowsWithTitle('VideoBackgroundAnimation12354951')
        if windows:
            # If the window exists, close it
            window = windows[0]
            window.close()

    def open_config():
        # Open the configuration window
        subprocess.run(['python', 'config_menu.py'])
        global config
        # Rereading the config
        with open("config.json", "r") as f:
            config = json.load(f)
        # Updating all the parameters
        config_changes()


    menu = Menu(MenuItem("Config", open_config), MenuItem('Exit', on_exit))
    icon = Icon("Pygame Zero App", create_image(), "AnimatedWallpaper", menu)
    icon.run()

def start_tray_thread():
    global system_tray_started
    if not system_tray_started:
        threading.Thread(target=setup_system_tray, daemon=True).start()
        system_tray_started = True

# Call the function to start the thread
start_tray_thread()

# Setting the screen resolution to full screen dynamically
monitor = get_monitors()[0]
width, height = monitor.width, monitor.height-10
# Setting the window position
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

import pgzrun

WIDTH = width
HEIGHT = height
TITLE = "VideoBackgroundAnimation12354951"

# Reading the config
with open("config.json", "r") as f:
    config = json.load(f)
# Getting the user's username
username = os.getlogin()

# Sets up the config on start
config_changes()

# Allowing for the vid to beging
frame_surface = None

win = pygame.display.get_wm_info()['window']
oldtime_ = time.time()
oldtime = time.time()
oldwin = None
def update():
    global FPS, frame_surface, video_path, oldtime, win, oldwin
    if window_maximized():
        acttime = time.time()
        if acttime >= oldtime+1/FPS:
            if oldwin == None:
                ctypes.windll.user32.SetWindowPos(win, 1, 0, 0, 0, 0, 0x0002)
                if gw.getActiveWindowTitle() != "VideoBackgroundAnimation12354951" and gw.getActiveWindowTitle() != None:
                    oldwin = gw.getWindowsWithTitle(gw.getActiveWindowTitle())
            else:
                try:
                    oldwin = if_pgz_active_win(oldwin)
                except:
                    pass
            # Check if we need to read the next frame
            if frame_surface is None:
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video from the beginning if it reaches the end
                    ret, frame = cap.read()
                    
                # Convert BGR to RGB (OpenCV uses BGR by default)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                # Create a surface from the frame
                frame_surface = pygame.surfarray.make_surface(frame_rgb)
                    
                # Rotate the image so it has a correct rotation
                frame_surface = pygame.transform.rotate(frame_surface, -90)

                # Flip the image so it's not mirrored
                frame_surface = pygame.transform.flip(frame_surface, True, False)

                # Resize the frame to fit the window
                frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))

                oldtime = acttime

    if keyboard.lctrl:
        if keyboard.l:
            exit()
        if keyboard.r:
            video_path = vid_reload()


def draw():
    global frame_surface
    if window_maximized():
        if frame_surface:
            screen.blit(frame_surface, (0, 0))  # Display the frame
            frame_surface = None




pgzrun.go()