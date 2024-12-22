import os
import cv2

# Returning a list of images with a specific path
def get_images(current):
    path = f"images/{current}"
    files = os.listdir(path)
    images = [file for file in files if file.endswith('.png')]
    return images

# Transforming a video into images in a specific path
def make_images(path):
    # Reading the video
    video = cv2.VideoCapture(path)
    frame_list = []
    frame_count = 0
    while video.isOpened():
        ret, frame = video.read()  # Capture frame-by-frame
        if ret:
            # Add the frame to the list
            frame_list.append(frame)
            frame_count += 1
        else:
            break
    video.release()
    
    # Saving images
    count = 0
    while True:
        if os.path.exists(f"images/{count}"):
            count += 1
        else:
            break
    
    save_path = f"images/{count}"
    # Making the directory
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # Save each frame as a .png file
    for frame_count, frame in enumerate(frame_list):
        # Construct the filename
        frame_filename = os.path.join(save_path, f'frame_{frame_count:04d}.png')
        
        # Save the frame as a .png file
        cv2.imwrite(frame_filename, frame)
    
    # Desinstalling the video
    video_path = f"{path}/vid_install.mp4"
    if os.path.exists(video_path):
        os.remove(video_path)
