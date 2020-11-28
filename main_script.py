import numpy as np
import cv2 as cv
import sys
from time import sleep

# Print numpy arrays fullsize, without ...
np.set_printoptions(threshold=sys.maxsize)

# Open the video as a stream;
# WARNING: I didn't upload the original video to the repo since it's large,
# but this code implies it's on the path. So I put it into .gitignore
vidcap = cv.VideoCapture('vid.mp4')

# Save image dimensions
height = int(vidcap.get(cv.CAP_PROP_FRAME_WIDTH))  # 720
width = int(vidcap.get(cv.CAP_PROP_FRAME_HEIGHT))  # 1280

# fps and number of frames in the video
fps = vidcap.get(cv.CAP_PROP_FPS)                  # 30
nframe = int(vidcap.get(cv.CAP_PROP_FRAME_COUNT))  # 4768

# Print the video characteristics
print(f'FPS: {fps}')
print(f'Number of frames: {nframe}')
print(f'Image width: {width}')
print(f'Image height: {height}')

# Explaining coordinates for cropping (take it as matrix indices).
# Note that the video is transposed inside the loop.
x = 290  # horizontal coordinate of the top-left corner
w = 120  # width (from left to right)
y = 400  # vertical coordinate of the top-left corner
h = 700  # height (from top to bottom)
# With this values defined, cropping would look like img[x : x + w, y : y + h]
# The numbers above give the crop with the whole bottle except the bottom.
# Below I used some other numbers directly for qiuck editing.

# Current frame number
curr_nframe = 0
# Background frame number (where there're no balls yet but it's already stable)
background_nframe = 610
# Writing y-coordinate and number of the corresponding frame to a csv file
datafile = open('video_raw_data.csv', 'a')

# Read the stream
while vidcap.isOpened():
    success, colored_frame = vidcap.read()
    if not success or curr_nframe > 4000:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    curr_nframe += 1  # starting from 1
    if curr_nframe < background_nframe:
        continue

    # The full-size grayscale frame
    frame = cv.cvtColor(colored_frame, cv.COLOR_BGR2GRAY)
    # Leave only the working area: the bottle from the 250 to 30 notches.
    frame = frame[310:390, 520:1100]  # <-> x, w, y, h = 310, 80, 520, 580

    # Save one frame from until the balls hasn't started to fall
    # to have a static picture of the ruler. It'll be subtracted later.
    if curr_nframe == background_nframe:
        background = frame
        cv.imwrite('background.png', background.transpose())

    # Subtract the background
    frame = cv.add(frame, cv.bitwise_not(background))

    # Invert the colors for the ball to be white
    frame = cv.bitwise_not(frame)

    # Threshold the frame. Pixels greater than the 2nd argument become 255.
    frame = cv.threshold(frame, 150, 255, cv.THRESH_BINARY)[1]

    # Errode and dilate a couple of times to avoid unwanted blobs
    frame = cv.dilate(frame, None, iterations=6)
    frame = cv.erode(frame, None, iterations=5)

    # The pre-processing stage has finished. Get the coordinate.
    ball_y_coords = frame.nonzero()[1]

    if ball_y_coords.size != 0:
        if np.amax(ball_y_coords) - np.amin(ball_y_coords) > 20:
            print('There is an extra white blob, probably a bubble. Erase it.')
            print(f'Frame number is {curr_nframe}.')
            sleep(5)
        else:
            datafile.write(f'{np.mean(ball_y_coords)},{curr_nframe}\n')

    # Press q to quit, printing the number of the last frame displayed
    if cv.waitKey(1) == ord('q'):
        print(curr_nframe)
        break

    # Display the current frame
    cv.imshow('frames', frame.transpose())

vidcap.release()
cv.destroyAllWindows()
datafile.close()
