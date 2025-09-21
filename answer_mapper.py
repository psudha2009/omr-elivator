import cv2
import numpy as np

def get_darkness(gray_image, contour):
    """
    Calculates the average pixel intensity inside a bubble contour.
    Lower intensity = darker = more likely filled.
    """
    mask = np.zeros(gray_image.shape, dtype="uint8")
    cv2.drawContours(mask, [contour], -1, 255, -1)
    mean_val = cv2.mean(gray_image, mask=mask)[0]
    return mean_val

def map_bubbles_to_answers(bubble_data, gray_image, mapping, set_id="A"):
    """
    Maps detected bubbles to answers using darkness detection.
    Assumes every 4 bubbles = 1 question.
    Sorts bubbles top-to-bottom, then left-to-right.
    """
    options = ["a", "b", "c", "d"]
    answers = []

    # Sort bubbles top-to-bottom, then left-to-right
    sorted_bubbles = sorted(bubble_data, key=lambda b: b["center"][1]*1000 + b["center"][0])

    for i in range(0, len(sorted_bubbles), 4):
        group = sorted_bubbles[i:i+4]
        if len(group) < 4:
            continue  # Skip incomplete questions

        # Sort left-to-right within the group
        group_sorted = sorted(group, key=lambda b: b["center"][0])

        # Measure darkness of each bubble
        darkness_values = [get_darkness(gray_image, b["contour"]) for b in group_sorted]
        marked_index = darkness_values.index(min(darkness_values))  # Darkest bubble

        raw_choice = options[marked_index]
        mapped_choice = mapping.get(set_id, {}).get(raw_choice, raw_choice)
        answers.append(mapped_choice)

    return answers