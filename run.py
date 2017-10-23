import time
import numpy as np
import argparse
import cv2
from numpy import empty, nan
import os
import sys
import time
import util
import CMT


CMT = CMT.CMT()
parser = argparse.ArgumentParser(description='Track an object.')
parser.add_argument('inputpath', nargs='?', help='The input path.')
args = parser.parse_args()

    # Clean up
cv2.destroyAllWindows()

if args.inputpath is not None:
    if os.path.isfile(args.inputpath):
        cap = cv2.VideoCapture(args.inputpath)
    # Otherwise assume it is a format string for reading images	
    # By default do not show preview in both cases
else:
    # If no input path was specified, open camera device
    cap = cv2.VideoCapture(0)

# Check if videocapture is working
if not cap.isOpened():
    print 'Unable to open video input.'
    sys.exit(1)

while True:
    status, im = cap.read()
    cv2.imshow('Preview', im)
    k = cv2.waitKey(10)
    if not k == -1:
        break

# Read first frame

# look up table 
x_weight = 0.29
x_bias = 0.5
y_weight = 0.43
y_bias = 0.8

status, im0 = cap.read()
full_size = im0.shape

x_arr = [i * x_weight + x_bias for i in xrange(full_size[1])]
y_arr = [i * y_weight + y_bias for i in xrange(full_size[0])]

#

im_gray0 = cv2.cvtColor(im0, cv2.COLOR_BGR2GRAY)
im_draw = np.copy(im0)

(tl, br) = util.get_rect(im_draw)

print 'using', tl, br, 'as init bb'
CMT.initialise(im_gray0, tl, br)

while True:
        # Read image
    tic1 = time.time()
    status, im = cap.read()
    if not status:
        break
    im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    im_draw = np.copy(im)

    picture_size_x = len(im_draw[0])
    picture_size_y = len(im_draw)
    center_point_in_frame_x = picture_size_x / 2  
    center_point_in_frame_y = picture_size_y / 2 

    tic = time.time()
    CMT.process_frame(im_gray)
    toc = time.time()

    # Draw updated estimate
    if CMT.has_result:
        cv2.line(im_draw, CMT.tl, CMT.tr, (255, 0, 0), 4)
        cv2.line(im_draw, CMT.tr, CMT.br, (255, 0, 0), 4)
        cv2.line(im_draw, CMT.br, CMT.bl, (255, 0, 0), 4)
        cv2.line(im_draw, CMT.bl, CMT.tl, (255, 0, 0), 4)
        
        Centerpoint_in_box = [(CMT.tr[0] + CMT.tl[0]) / 2 , (CMT.br[1] + CMT.tr[1]) / 2]

    #############################
    # key point draw
    #util.draw_keypoints(self.CMT.tracked_keypoints, im_draw, (255, 255, 255))
    # this is from simplescale
    #util.draw_keypoints(self.CMT.votes[:, :2], im_draw)  # blue
    #util.draw_keypoints(self.CMT.outliers[:, :2], im_draw, (0, 0, 255))

    # cv2.imshow('main', im_draw)
    #cv2.imshow('main', im_gray)

    # Check key input
    k = cv2.waitKey(10)
    key = chr(k & 255)
    if key == 'q':
        break
    if key == 'r':
        # 'r' key means that a user wanna reset the rectangle.
        # cv2.destroyAllWindows()
        (tl, br) = util.get_rect(im_draw)
        CMT.initialise(im_gray, tl, br)
        print 'using', tl, br, 'as reset bb'
        
    # Remember image
    im_prev = im_gray

    # print 'center: {0:.2f},{1:.2f} scale: {2:.2f}, active: {3:03d}, {4:04.0f}ms'.format(self.CMT.center[0], self.CMT.center[1], self.CMT.scale_estimate, self.CMT.active_keypoints.shape[0], 1000 * (toc - tic))

    if str(CMT.center[0]) != 'nan' and str(CMT.center[1]) != 'nan':
        print 'Current center point in frame : (%s, %s)' % (str(center_point_in_frame_x), str(center_point_in_frame_y))
        print 'Current center point in recognized box : (%s, %s)' % (str(Centerpoint_in_box[0]),str(Centerpoint_in_box[1]))

        move_point_x = Centerpoint_in_box[0] - center_point_in_frame_x 
        move_point_y = Centerpoint_in_box[1] - center_point_in_frame_y 

        if move_point_x > 0:
            direction_x = 'right'
        else:
            direction_x = 'left'

        if move_point_y > 0:
            direction_y = 'up'
        else:
            direction_y = 'down'
            
        print 'To locate the tracked box to center, please move %s point to %s and %s point to %s \n' % (str(abs(move_point_x)), str(direction_x), str(abs(move_point_y)), str(direction_y))
        print 'look up table \nx value :%s %s \ny value :%s %s \n\n' % (direction_x, str(x_arr[abs(move_point_x)]), direction_y, str(y_arr[abs(move_point_x)]))

        # draw arrow
        cv2.arrowedLine(im_draw, (Centerpoint_in_box[0], Centerpoint_in_box[1]), (center_point_in_frame_x, Centerpoint_in_box[1]), (0,0,255), 3) # x draw
        cv2.arrowedLine(im_draw, (center_point_in_frame_x, Centerpoint_in_box[1]), (center_point_in_frame_x, center_point_in_frame_y), (0,0,255), 3) # y draw
        cv2.circle(im_draw, (center_point_in_frame_x, center_point_in_frame_y), 40, (0, 255, 255), 1)
    else:
        print "Coudln't track or find the object." 
        
    print 'Processing time :%s' % str(time.time()-tic1)
    cv2.imshow('main', im_draw)
    
