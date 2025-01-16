import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time
import os

# Setup
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)

offset = 20
imgSize = 300
folder = "Data/D"
os.makedirs(folder, exist_ok=True)

counter = 0

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']

        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
        x1, y1 = max(0, x - offset), max(0, y - offset)
        x2, y2 = min(img.shape[1], x + w + offset), min(img.shape[0], y + h + offset)
        imgCrop = img[y1:y2, x1:x2]

        try:
            aspectRatio = h / w

            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize

            cv2.imshow("Image Cropped", imgCrop)
            cv2.imshow("Image White", imgWhite)

        except Exception as e:
            print("Error processing the image:", e)

    # Display counter on the main image
    cv2.putText(img, f'Images Saved: {counter}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                1, (0, 255, 0), 2)
    cv2.imshow('Image', img)

    key = cv2.waitKey(1)
    if key == ord("s"):
        counter += 1
        cv2.imwrite(f'{folder}/Image_{time.time()}.jpg', imgWhite)
        print(f"Image saved: {counter}")
    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
