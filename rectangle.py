import cv2
import numpy as np


def nothing(x):
    pass


cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Trackbars", 300, 500)

cv2.createTrackbar("Hue min", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("Hue max", "Trackbars", 179, 179, nothing)

cv2.createTrackbar("Sat min", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("Sat max", "Trackbars", 255, 255, nothing)

cv2.createTrackbar("Val min", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("Val max", "Trackbars", 255, 255, nothing)


cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Camera not found!")
    exit()

kernel = np.ones((5, 5), np.uint8)


while True:

    ret, frame = cam.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h_min = cv2.getTrackbarPos("Hue min", "Trackbars")
    h_max = cv2.getTrackbarPos("Hue max", "Trackbars")

    s_min = cv2.getTrackbarPos("Sat min", "Trackbars")
    s_max = cv2.getTrackbarPos("Sat max", "Trackbars")

    v_min = cv2.getTrackbarPos("Val min", "Trackbars")
    v_max = cv2.getTrackbarPos("Val max", "Trackbars")

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    mask = cv2.inRange(hsv, lower, upper)

    mask = cv2.erode(
        mask,
        kernel,
        iterations=1
    )

    mask = cv2.dilate(
        mask,
        kernel,
        iterations=2
    )

    opening = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    closing = cv2.morphologyEx(
        opening,
        cv2.MORPH_CLOSE,
        kernel
    )

    contours, _ = cv2.findContours(
        closing,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < 1000:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2
        )

        cx = int(x + w / 2)
        cy = int(y + h / 2)

        cv2.circle(
            frame,
            (cx, cy),
            5,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            frame,
            f"Center: ({cx}, {cy})",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Area: {int(area)}",
            (x, y + h + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

    cv2.imshow("Camera", frame)
    cv2.imshow("Mask", closing)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or key == 27:
        break


cam.release()
cv2.destroyAllWindows()