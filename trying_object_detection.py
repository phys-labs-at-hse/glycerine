import numpy as np
import cv2 as cv

img = cv.imread('img_with_objects.png', cv.IMREAD_GRAYSCALE)
height, width = img.shape

print(f'height: {height}')
print(f'width: {width}')

np.mean(img.nonzero()[0])
np.sum(img)/255

## Display the current frame
#cv.waitKey(0)
#cv.imshow('Image', img)
#cv.destroyAllWindows()


## Save one frame to play with object detection functions.
#if curr_nframe == 2206:
#    cv.imwrite('img_with_objects.png', frame.transpose())
