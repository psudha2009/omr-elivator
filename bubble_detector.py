import cv2
import numpy as np

def detect_bubbles(image):
    """
    Detect bubbles from a scanned OMR sheet.
    Accepts a PIL image or file path.
    Returns:
        - bubble_data: list of dicts with 'center' and 'contour'
        - gray: grayscale image for darkness analysis
    """
    # Convert PIL image to OpenCV format if needed
    if not isinstance(image, str):
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    else:
        image = cv2.imread(image)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding to highlight filled bubbles
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bubble_data = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 100 < area < 1000:  # Filter by area to exclude noise
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            circularity = 4 * np.pi * area / (cv2.arcLength(cnt, True) ** 2)
            if circularity > 0.7:  # Roughly circular
                bubble_data.append({
                    "center": (int(x), int(y)),
                    "contour": cnt
                })

    # Sort bubbles top-to-bottom, then left-to-right
    bubble_data.sort(key=lambda b: (b["center"][1], b["center"][0]))

    return bubble_data, gray