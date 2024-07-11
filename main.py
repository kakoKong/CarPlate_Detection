import cv2 
from check_plate import PlateFinder
from ocr import OCR


if __name__ == "__main__": 
	
	findPlate = PlateFinder(minPlateArea=2000, 
								maxPlateArea=7000) 
	# model = OCR(modelFile="<Path to OCR Model>", 
		#          labelFile="<Path to File>") 
	img = cv2.imread('frame2.png')
	cv2.imshow('original_image', img)
	possible_plates = findPlate.find_possible_plates(img)
	for i in range(len(possible_plates)):
		cv2.imshow(f'possible plate ${i+1}', possible_plates[i])
		chars_on_plate = findPlate.char_on_plate[i]
		for j in range(len(chars_on_plate)):
			if (i == 0):
				cv2.imshow(f'chars on plate ${i+1}, ${j+1}', chars_on_plate[j])
	# print('possible plate', possible_plates)

	# cap = cv2.VideoCapture('video.mp4') 
	
	# while (cap.isOpened()): 
	# 	ret, img = cap.read() 
		
	# 	if ret == True: 
	# 		cv2.imshow('original video', img) 
			
	# 		if cv2.waitKey(25) & 0xFF == ord('q'): 
	# 			break
	# 		print("Not beak")
	# 		possible_plates = findPlate.find_possible_plates(img) 
	# 		if possible_plates is not None: 
	# 			print("not none!")
	# 			for i, p in enumerate(possible_plates): 
	# 				chars_on_plate = findPlate.char_on_plate[i] 
	# 				print("Wassup")
	# 				# recognized_plate, _ = model.label_image_list( 
	# 				# 		chars_on_plate, imageSizeOuput = 128) 

	# 				# print(recognized_plate) 
	# 				cv2.imshow('plate', p) 
					
	# 				if cv2.waitKey(25) & 0xFF == ord('q'): 
	# 					break
	# 	else: 
	# 		break
			
	# cap.release() 
 
while True:
		k = cv2.waitKey(0) & 0xFF
		# print(k)
		if k == 27 or k == ord('q'):
				cv2.destroyAllWindows()
				break
