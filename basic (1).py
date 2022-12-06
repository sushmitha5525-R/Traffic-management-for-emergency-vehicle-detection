import cv2
src = cv2.imread("Photos/ambulance.jpg")
image = cv2.flip(src, 1)
half = cv2.resize(image, (0, 0), fx = 0.1, fy = 0.1)
cv2.imshow("pic",half)
cv2.waitKey(0)
