# CarPlate_Detector
## Source
This project is made possible thanks to this article: https://www.geeksforgeeks.org/detect-and-recognize-car-license-plate-from-a-video-in-real-time/?ref=lbp

## Dev

This project is consisted of 2 main ML section
1. Plate Detection (Object Detection)
2. OCR (Character Recognition)

### Plate Detection
The PlateFinder class will be focusing on detecting the plate in the image, or in this case a frame in video. In order to be able to detect the plate, we will be using Contours Extraction technique.
Where we can look into function in this order:
1. Pre_processing

1.1 Image Blurring

1.2 Convert to Gray Scale

1.3 Sobel function to get verticle edges

1.4 Add an threshold

1.5 Morphology: Closing = Expand pixels (Dilation), then shrink (Erosion)

2. Extract_contours
2.1 Find Contours (shape)

3. Check_plate
3.1 Get Minimum Rectangle Area

3.2 Validate Ratio

3.3 Clean Plate

  3.3.1 Convert Color

  3.3.2 Add threshold

  3.3.3 Find Contours
  
  3.3.4 Get Area of plate => Create Regtangle amd return the coordinates