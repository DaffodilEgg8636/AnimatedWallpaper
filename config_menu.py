import pgzrun
import pgzero, pygame
import json
from screeninfo import get_monitors
import time


# Setting the screen resolution to half screen dynamically
monitor = get_monitors()[0]
width, height = monitor.width, monitor.height-10
WIDTH = width/2
HEIGHT = height/2

# Reading the config
with open("config.json", "r") as f:
	config = json.load(f)
	

# Creates the configurator data
configs = []
count = 0
for i, key in enumerate(config):
	configs.append(key)
multiplyer = 1


def draw():
	global count, config
	screen.clear()
	# Creates the visuals of the configurator
	selector = Rect((0, 20+count*30), (5, 20))  # (x, y) position and (width, height)
	for i, key in enumerate(config):
		screen.draw.text(key, color="white", pos=(20, 20+i*30), fontsize=30)
	for i, key in enumerate(config):
		screen.draw.text(str(config[key]), color="white", pos=(WIDTH/2, 20+i*30), fontsize=30)
	screen.draw.rect(selector, color="white")


def update():
	global multiplyer, oldtime, config
	if keyboard.lshift:
		multiplyer = 10
	else:
		multiplyer = 1
		

def on_key_down():
	global config, count, configs, multiplyer
	# Functionnality of the configurator
	if configs != []:
		if keyboard.up:
			if count == 0:
				count = len(configs)-1
			else:
				count -= 1
		if keyboard.down:
			if count == len(configs)-1:
				count = 0
			else:
				count += 1
		if keyboard.right:
			config[configs[count]] += 1*multiplyer
		if keyboard.left:
			if config[configs[count]] >= 0+multiplyer:
				config[configs[count]] -= 1*multiplyer
	if keyboard.RETURN:
		with open("config.json", "w") as f:
			json.dump(config, f)
		exit()









pgzrun.go()