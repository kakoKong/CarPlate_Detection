import cv2 
import numpy as np 
import easyocr
import os

from utils import segment_chars 

class PlateFinder: 
	def __init__(self, minPlateArea, maxPlateArea): 
		
		# minimum area of the plate 
		self.min_area = minPlateArea 
		
		# maximum area of the plate 
		self.max_area = maxPlateArea 

		self.element_structure = cv2.getStructuringElement( 
							shape = cv2.MORPH_RECT, ksize =(22, 3)) 

	def preprocess(self, input_img): 
		
		imgBlurred = cv2.GaussianBlur(input_img, (7, 7), 0) 
		
		# convert to gray 
		gray = cv2.cvtColor(imgBlurred, cv2.COLOR_BGR2GRAY) 
		
		# sobelX to get the vertical edges 
		sobelx = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize = 3) 
		
		# otsu's thresholding 
		ret2, threshold_img = cv2.threshold(sobelx, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) 
		
		element = self.element_structure 
		morph_n_thresholded_img = threshold_img.copy() 
		
		cv2.morphologyEx(src = threshold_img, 
						op = cv2.MORPH_CLOSE, 
						kernel = element, 
						dst = morph_n_thresholded_img) 
		cv2.imshow("morphology", morph_n_thresholded_img)
		return morph_n_thresholded_img 

	def extract_contours(self, after_preprocess): 
		
		contours, _ = cv2.findContours(after_preprocess, 
										mode = cv2.RETR_EXTERNAL, 
										method = cv2.CHAIN_APPROX_NONE) 
		return contours 

	def clean_plate(self, plate): 
		
		gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY) 
		thresh = cv2.adaptiveThreshold(gray, 
									255, 
									cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
									cv2.THRESH_BINARY, 
									11, 2) 
		
		contours, _ = cv2.findContours(thresh.copy(), 
										cv2.RETR_EXTERNAL, 
										cv2.CHAIN_APPROX_NONE) 

		if contours: 
			areas = [cv2.contourArea(c) for c in contours] 
			print("contoursss")
			print("areas", areas)
			# index of the largest contour in the area 
			# array 
			max_index = np.argmax(areas) 

			max_cnt = contours[max_index] 
			max_cntArea = areas[max_index] 
			x, y, w, h = cv2.boundingRect(max_cnt) 
			rect = cv2.minAreaRect(max_cnt) 
			# if not self.ratioCheck(max_cntArea, plate.shape[1], 
			# 									plate.shape[0]): 
			# 	return plate, False, None
			
			return plate, True, [x, y, w, h] 
		
		else: 
			return plate, False, None



	def check_plate(self, input_img, contour): 
		
		min_rect = cv2.minAreaRect(contour) 
		
		if self.validateRatio(min_rect): 
			x, y, w, h = cv2.boundingRect(contour) 
			after_validation_img = input_img[y:y + h, x:x + w] 
			after_clean_plate_img, plateFound, coordinates = self.clean_plate( 
														after_validation_img) 
			print('Checking plate...')
			print(coordinates)
			# cv2.imshow("after_check_plate_img", after_check_plate_img)
			if plateFound: 
				print("found Plate")
				characters_on_plate = self.find_characters_on_plate( 
											after_clean_plate_img) 
				# print(characters_on)
				if (characters_on_plate is not None and len(characters_on_plate) == 8): 
					x1, y1, w1, h1 = coordinates 
					coordinates = x1 + x, y1 + y 
					after_check_plate_img = after_clean_plate_img 
					print("checking image")
					
					return after_check_plate_img, characters_on_plate, coordinates 
		
		return None, None, None



	def find_possible_plates(self, input_img): 
		
		""" 
		Finding all possible contours that can be plates 
		"""
		plates = [] 
		self.char_on_plate = [] 
		self.corresponding_area = [] 

		self.after_preprocess = self.preprocess(input_img) 
		possible_plate_contours = self.extract_contours(self.after_preprocess) 

		for cnts in possible_plate_contours: 
			# print("lalala")
			plate, characters_on_plate, coordinates = self.check_plate(input_img, cnts) 
			print(plate)
			
			if plate is not None: 
				plates.append(plate) 
				self.char_on_plate.append(characters_on_plate) 
				self.corresponding_area.append(coordinates) 

		if (len(plates) > 0): 
			return plates 
		
		else: 
			print("none")
			return None

	def find_characters_on_plate(self, plate): 

		charactersFound = segment_chars(plate, 20) 
		print(charactersFound)
		print("found character?")
		if charactersFound: 
			return charactersFound 

	# PLATE FEATURES 
	def ratioCheck(self, area, width, height): 
		
		min = self.min_area 
		max = self.max_area 

		ratioMin = 3
		ratioMax = 6

		ratio = float(width) / float(height) 
		
		if ratio < 1: 
			ratio = 1 / ratio 
		
		if (area < min or area > max) or (ratio < ratioMin or ratio > ratioMax): 
			return False
		
		return True

	def preRatioCheck(self, area, width, height): 
		
		min = self.min_area 
		max = self.max_area 

		ratioMin = 2.5
		ratioMax = 7

		ratio = float(width) / float(height) 
		
		if ratio < 1: 
			ratio = 1 / ratio 

		if (area < min or area > max) or (ratio < ratioMin or ratio > ratioMax): 
			return False
		
		return True

	def validateRatio(self, rect): 
		(x, y), (width, height), rect_angle = rect 

		if (width > height): 
			angle = -rect_angle 
		else: 
			angle = 90 + rect_angle 

		if angle > 15: 
			return False
		
		if (height == 0 or width == 0): 
			return False

		area = width * height 
		
		if not self.preRatioCheck(area, width, height): 
			return False
		else: 
			return True
