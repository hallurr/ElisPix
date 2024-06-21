import cv2
import numpy as np
import math
from image_utils import crop_image
from scipy.optimize import minimize

min_object_ratio = 0.1
corner_threshold = 235


def rotate_image(img):
    img = crop_image(img)
    mask = get_mask(img, corner_threshold, 255)
    angle = optimal_rotation(mask)
    M = cv2.getRotationMatrix2D(
        (img.shape[1] / 2, img.shape[0] / 2), angle, 1)
    img = cv2.warpAffine(
        img, M, (img.shape[1], img.shape[0]), borderValue=(255, 255, 255))
    img = crop_image(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def optimal_rotation(mask):
    starting_angle = get_starting_angle(mask)
    result = minimize(pixel_diff, [starting_angle], args=(mask,),  bounds=[(-45, 45)],
                      options={'finite_diff_rel_step': 0.5, 'accuracy': 0.01, 'eps': 0.1})
    return result.x[0] if result.success else 0


def pixel_diff(angle, img):
    try:
        M = cv2.getRotationMatrix2D(
            (img.shape[1] / 2, img.shape[0] / 2), angle[0], 1)
        rotated_img = cv2.warpAffine(
            img, M, (img.shape[1], img.shape[0]), borderValue=(255, 255, 255))

        pixel_difference = np.sum(img == 0) - np.sum(rotated_img == 0)
        if pixel_difference > 0:
            return 1e4 * pixel_difference

        rotated_img = crop_image(rotated_img)
        nonpixel_difference = np.sum(
            img == 255) - np.sum(rotated_img == 255)

        ratio = nonpixel_difference / \
            (pixel_difference if pixel_difference != 0 else 1)
        return ratio * math.copysign(1, angle[0])
    except Exception as e:
        print(f"Error in pixel_diff: {e}")
        return 1e9


def get_starting_angle(mask):
    left_result = pixel_diff([-0.5], mask)
    right_result = pixel_diff([0.5], mask)
    if left_result < right_result:
        return 0.5
    elif right_result > left_result:
        return -0.5
    else:
        return 0.5


def get_mask(img, lower_threshold, upper_threshold):
    lower_threshold = np.array([lower_threshold] * 3)
    upper_threshold = np.array([upper_threshold] * 3)
    mask = cv2.inRange(img, lower_threshold, upper_threshold)
    mask = cv2.bitwise_not(mask)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = min_object_ratio * img.shape[1]
    filtered_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[
        2] >= min_width]
    mask = np.zeros_like(mask)
    cv2.drawContours(mask, filtered_contours, -1,
                     255, thickness=cv2.FILLED)
    mask = cv2.bitwise_not(mask)
    return mask
