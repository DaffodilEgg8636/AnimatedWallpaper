import json
import pygetwindow as gw

# Reading the config
with open("config.json", "r") as f:
    config = json.load(f)

# Making variables global to avoid memory usage
opti = None
oldwin = None

# Setting the function for video reloading/changing
def vid_reload():
	global config
	return f'videos/{config["current"]}'


# Looking if the user is using an app that is in fullscreen
def window_maximized():
	global opti
	# Get all the open windows
	windows = gw.getAllWindows()

	opti = True
#    for window in windows:
#        # Check if any window is maximized (potentially fullscreen)
#        if window.isVisible and window.title != "VideoBackgroundAnimation12354951":
#            opti = False
	active_window = gw.getActiveWindow()
	if (active_window == None or active_window.title != "VideoBackgroundAnimation12354951"):
		if active_window != None and active_window.isMaximized:
			opti = False

	locals().clear()
	return opti

# Going to the previously used window if the pgz win selected
def if_pgz_active_win(oldwin):
	actwin = gw.getActiveWindow()
	if actwin != None:
		if actwin.title == "VideoBackgroundAnimation12354951":
			oldwin[0].activate()
			return oldwin
		else:
			locals().clear()
			return gw.getWindowsWithTitle(gw.getActiveWindowTitle())
	else:
		locals().clear()
		return oldwin
