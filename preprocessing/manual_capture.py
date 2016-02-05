import cv2


capture = cv2.VideoCapture(0)

c = True
i = 0
while c != 27:
	status, frame = capture.read()
	cv2.imshow('img',frame)
	c = cv2.waitKey(2) & 0xFF

	if c == ord('w'):
		cv2.imwrite('../temp_images/%s_sample.png' % str(i), frame)
		i += 1

capture.release()
cv2.destroyAllWindows()