import pgzrun
import pgzero
import pygame
import time
import json
import os
import cv2

# Importing custom libraries
from classes import *
from functions import *

# Setting the screen resolution to full screen dynamically
screen_res = pygame.display.Info()
print(screen_res)
WIDTH = screen_res.current_w
HEIGHT = screen_res.current_h

# Reading the config
with open("config.json", "r") as f:
    config = json.load(f)
# Getting the user's username
username = os.getlogin()
# Getting the path for converting videos
path_video = ""
if config["videopath"] == "default":
    path_video = f"C:/Users/{username}/Desktop"
else:
    path_video = config["videopath"]

# Creating the animation of the wallpaper
wallpaper = Animation(get_images(config["current"]), config["fps"])



def draw():
    # Drawing the animation
    screen.blit(wallpaper.draw())


def update():
    global wallpaper, config
    # Updating the animation
    wallpaper.update()
    # User commands
    if keyboard.lctrl:
        if keyboard.lalt:
            # Reload the animation
            if keyboard.r:
                with open("config.json", "r") as f:
                    config = json.load(f)
                wallpaper.list_update(get_images(config["current"]))
            # Exit the programm
            if keyboard.escape:
                exit()
            # ?
            if keyboard.m:
                pass
                





pgzrun.go()