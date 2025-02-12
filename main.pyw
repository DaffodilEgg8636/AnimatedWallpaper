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
import gc
import weakref
import pyopencl as cl
import numpy as np

# Importing custom libraries
from classes import *
from functions import *


# Enable the garbage collector
gc.enable()

# Lower the process priority
p = psutil.Process(os.getpid())
p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)  
p = None; del p

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

icon_image = None
def create_image():
    global icon_image
    """Create an icon for the system tray."""
    icon_image = Image.new('RGB', (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle((16, 16, 48, 48), fill=(0, 0, 255))
    locals().clear()

def setup_system_tray():
    global icon_image
    """Set up the system tray icon and menu."""
    def on_exit(icon):
        icon.stop()
        # Stop the game when the tray icon menu is exited
        windows = gw.getWindowsWithTitle('VideoBackgroundAnimation12354951')
        if windows:
            # If the window exists, close it
            window = windows[0]
            window.close()
        locals().clear()

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
    create_image()
    icon = Icon("Pygame Zero App", icon_image, "AnimatedWallpaper", menu)
    icon.run()

def start_tray_thread():
    global system_tray_started
    if not system_tray_started:
        threading.Thread(target=setup_system_tray, daemon=True).start()
        system_tray_started = True

# Call the function to start the thread
start_tray_thread()
icon_image = None; del icon_image

# Setting the screen resolution to full screen dynamically
monitor = get_monitors()[0]
width, height = monitor.width, monitor.height-10
monitor = None; del monitor
# Setting the window position
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

import pgzrun

WIDTH = width
HEIGHT = height
width = None; del width
height = None; del height
TITLE = "VideoBackgroundAnimation12354951"

# Reading the config
with open("config.json", "r") as f:
    config = json.load(f)

# Sets up the config on start
config_changes()

# Allowing for the vid to beging
frame = None


# Create an OpenCL context
platform = cl.get_platforms()[0]  # Select the first platform (e.g., NVIDIA, AMD)
device = platform.get_devices()[0]  # Select the first device (GPU or CPU)
context = cl.Context([device])
queue = cl.CommandQueue(context)

# OpenCL kernel to rotate and flip the image
transform_kernel = """
__kernel void transform_image(__global uchar *in_image, 
                              __global uchar *out_image,
                              const unsigned int in_width, 
                              const unsigned int in_height,
                              const unsigned int out_width, 
                              const unsigned int out_height) {

    int i = get_global_id(0);  // X-coordinate in output
    int j = get_global_id(1);  // Y-coordinate in output

    if (i < in_width && j < in_height) {
    
        int out_index = (j * out_width + i) * 3;
        int in_index = (j * in_width + (in_width - 1 - i)) * 3;
    
        out_image[out_index]     = in_image[in_index];  
        out_image[out_index + 1] = in_image[in_index + 1];  
        out_image[out_index + 2] = in_image[in_index + 2];  
        
        }
    }
}
"""

# Compile the OpenCL program
rotate_flip_cl = cl.Program(context, transform_kernel).build()


















win = pygame.display.get_wm_info()['window']
oldtime = time.time()
oldwin = None
def update_():
    global FPS, frame, video_path, oldtime, win, oldwin, oldtime_g, rotate_flip_cl
    acttime = time.time()
    if window_maximized():
        #if acttime >= oldtime+1/FPS:
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
        if frame is None:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video from the beginning if it reaches the end
                ret, frame = cap.read()
                    
            # Convert BGR to RGB (OpenCV uses BGR by default)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


            # Convert the frame to a numpy array
            input_image = np.array(frame, dtype=np.uint8)

            # Define the output dimensions (e.g., after rotation and flip)
            height, width, channels = frame.shape
            input_width = width
            input_height = height
            output_width = input_height
            output_height = input_width

            # Set up the output image buffer
            output_image = np.zeros((output_height, output_width, 3), dtype=np.uint8)

            # Create OpenCL buffers
            input_buffer = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=input_image)
            output_buffer = cl.Buffer(context, cl.mem_flags.WRITE_ONLY, size=output_image.nbytes)

            # Flattens the images into 1D arrays
            input_image = input_image.flatten()  # Convert from (H, W, 3) to (H * W * 3)
            output_image = output_image.flatten()
            
            # Execute the OpenCL kernel for image transformation (rotation + flip)
            global_work_size = (input_width, input_height)  # Use output dimensions
            rotate_flip_cl.transform_image(queue, global_work_size, None,  # `None` for local work size
                               input_buffer, output_buffer, 
                               np.uint32(input_width), np.uint32(input_height), 
                               np.uint32(output_width), np.uint32(output_height))

            # Read the result back into Python
            cl.enqueue_copy(queue, output_image, output_buffer).wait()

            # Convert the transformed image back to Pygame surface for rendering
            #frame = output_image.reshape((output_height, output_width, 3)
            frame = pygame.surfarray.make_surface(output_image)

            # Resize the image to the correct dimensions
            #frame = pygame.transform.scale(frame, (WIDTH, HEIGHT))


            # Create a surface from the frame
            #frame = pygame.surfarray.make_surface(frame)
                    
            # Rotate the image so it has a correct rotation
            #frame = pygame.transform.rotate(frame, -90)

            # Flip the image so it's not mirrored
            #frame = pygame.transform.flip(frame, True, False)

            #oldtime = acttime


    if gc.garbage:
        gc.collect()
    locals().clear()

# Set the FPS for the program loop
clock.schedule_interval(update_, 1 / FPS)



def draw():
    global frame
    if window_maximized():
        if frame:
            screen.blit(frame, (0, 0))  # Display the frame
            frame = None
    locals().clear()



pgzrun.go()
