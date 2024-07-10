import cv2 
import numpy as np
import imutils 

from skimage.filters import threshold_local 
from skimage import measure 

def sort_cont(character_contours): 
	""" 
	To sort contours 
	"""
	i = 0
	boundingBoxes = [cv2.boundingRect(c) for c in character_contours] 
	
	(character_contours, boundingBoxes) = zip(*sorted(zip(character_contours, 
														boundingBoxes), 
													key = lambda b: b[1][i], 
													reverse = False)) 
	
	return character_contours 


def segment_chars(plate_img, fixed_width): 
    """ 
    Extract Value channel from the HSV format of image and apply adaptive thresholding 
    to reveal the characters on the license plate 
    """
    V = cv2.split(cv2.cvtColor(plate_img, cv2.COLOR_BGR2HSV))[2]

    thresh = cv2.adaptiveThreshold(V, 255, 
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 
                                   11, 2) 
    
    thresh = cv2.bitwise_not(thresh) 

    # Resize the license plate region to a canonical size 
    plate_img = imutils.resize(plate_img, width=fixed_width) 
    thresh = imutils.resize(thresh, width=fixed_width) 
    bgr_thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR) 

    # Perform a connected components analysis 
    # and initialize the mask to store the locations of the character candidates 
    labels = measure.label(thresh, background=0) 

    charCandidates = np.zeros(thresh.shape, dtype='uint8') 

    # Loop over the unique components 
    characters = [] 
    for label in np.unique(labels): 
        
        # If this is the background label, ignore it 
        if label == 0: 
            continue
        # Otherwise, construct the label mask to display 
        # only connected components for the current label, 
        # then find contours in the label mask 
        labelMask = np.zeros(thresh.shape, dtype='uint8') 
        labelMask[labels == label] = 255

        cnts = cv2.findContours(labelMask, 
                                cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE) 

        cnts = cnts[1] if imutils.is_cv3() else cnts[0] 

        # Ensure at least one contour was found in the mask 
        if len(cnts) > 0: 

            # Grab the largest contour which corresponds 
            # to the component in the mask, then grab the 
            # bounding box for the contour 
            c = max(cnts, key=cv2.contourArea) 
            (boxX, boxY, boxW, boxH) = cv2.boundingRect(c) 

            # Compute the aspect ratio, solidity, and 
            # height ratio for the component 
            aspectRatio = boxW / float(boxH) 
            solidity = cv2.contourArea(c) / float(boxW * boxH) 
            heightRatio = boxH / float(plate_img.shape[0]) 

            # Determine if the aspect ratio, solidity, 
            # and height of the contour pass the rules 
            # tests 
            keepAspectRatio = aspectRatio < 1.0
            keepSolidity = solidity > 0.15
            keepHeight = heightRatio > 0.5 and heightRatio < 0.95

            # Check to see if the component passes 
            # all the tests 
            if keepAspectRatio and keepSolidity and keepHeight and boxW > 14: 
                
                # Compute the convex hull of the contour 
                # and draw it on the character candidates 
                # mask 
                hull = cv2.convexHull(c) 

                cv2.drawContours(charCandidates, [hull], -1, 255, -1) 

    contours, hier = cv2.findContours(charCandidates, 
                                      cv2.RETR_EXTERNAL, 
                                      cv2.CHAIN_APPROX_SIMPLE) 
    
    if contours: 
        contours = sort_cont(contours) 
        
        # Value to be added to each dimension 
        # of the character 
        addPixel = 4
        for i, c in enumerate(contours): 
            (x, y, w, h) = cv2.boundingRect(c) 
            if y > addPixel: 
                y = y - addPixel 
            else: 
                y = 0
            if x > addPixel: 
                x = x - addPixel 
            else: 
                x = 0
            temp = bgr_thresh[y:y + h + (addPixel * 2), 
                              x:x + w + (addPixel * 2)] 

            characters.append(temp) 
            
            # Visualize the characters
            cv2.imshow(f'Character {i+1}', temp)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        return characters 
    
    else: 
        return None