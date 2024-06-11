import numpy as np
import matplotlib.image
import matplotlib.pyplot
import cv2
import os
import pathlib

LOWER_WHITE = [215, 215, 215]
UPPER_WHITE = [255, 255, 255]
NEON_GREEN = [0, 255, 127]


def get_split_images(img):
    height, width, _ = img.shape
    pad_height = int(height * 0.1)
    pad_width = int(width * 0.1)
    img = cv2.copyMakeBorder(img, pad_height, pad_height, pad_width,
                             pad_width, cv2.BORDER_CONSTANT, value=UPPER_WHITE)
    contours, _ = get_mask(img)

    rectangles = []
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        x, y, w, h = cv2.boundingRect(box)
        if w >= width * 0.1 and h >= height * 0.1:  # filter out small objects
            rectangles.append(cnt)

    rectangle_coordinates = []
    for _, rect in enumerate(rectangles):
        rect2 = cv2.minAreaRect(rect)
        box = cv2.boxPoints(rect2)
        box = np.int0(box)
        x, y, w, h = cv2.boundingRect(box)
        x1 = x - pad_width
        y1 = y - pad_height
        x2 = x1 + w
        y2 = y1 + h
        rectangle_coordinates.append((y1, y2, x1, x2))
    return rectangle_coordinates


def get_mask(img):
    lower_white = np.array(LOWER_WHITE)
    upper_white = np.array(UPPER_WHITE)
    mask = cv2.inRange(img, lower_white, upper_white)
    mask = cv2.bitwise_not(mask)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_width = 0 * img.shape[1]

    filtered_contours = []
    for cnt in contours:
        _, _, w, _ = cv2.boundingRect(cnt)
        if w >= min_width:
            filtered_contours.append(cnt)

    mask = np.zeros_like(mask)
    cv2.drawContours(mask, filtered_contours, -1, (255), thickness=cv2.FILLED)
    mask = cv2.bitwise_not(mask)
    return filtered_contours, mask


def get_rotation_angle(coordinates, image_width, image_height):
    x1, y1, x2, y2 = coordinates

    if x2 < x1:
        x1, y1, x2, y2 = x2, y2, x1, y1

    dy = (y2 - y1) / image_height
    dx = (x2 - x1) / image_width

    rotation_angle = np.arctan(dy / dx)
    rotation_angle_deg = np.degrees(rotation_angle)

    if rotation_angle_deg >= 0:
        minimal_rotation_angle = 90 - rotation_angle_deg
    else:
        minimal_rotation_angle = 90 + rotation_angle_deg

    print('Coordinates:', coordinates, ', angle:', minimal_rotation_angle)
    return minimal_rotation_angle


def rotate_image(image, coordinates):
    # image, angle = get_strongest_side(image, mask)
    angle = get_rotation_angle(coordinates, image.shape[1], image.shape[0])

    image_size = (image.shape[1], image.shape[0])
    image_center = tuple(np.array(image_size) / 2)

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1)

    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])
    bound_w = int(image_size[0] * abs_cos + image_size[1] * abs_sin)
    bound_h = int(image_size[0] * abs_sin + image_size[1] * abs_cos)

    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    rotated_image = cv2.warpAffine(
        image, rotation_mat, (bound_w, bound_h), borderValue=(UPPER_WHITE))
    return rotated_image


class ImageProcessor:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.initialize_folders()

    def initialize_folders(self):
        if not os.path.exists(self.input_folder):
            os.makedirs(self.input_folder)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def process_images(self):
        pic_list = list(pathlib.Path(self.input_folder).glob('*.tif'))
        for pic_index in range(len(pic_list)):
            img = cv2.imread(str(pic_list[pic_index]))
            image_coordinates = get_split_images(img)
            print(
                f'Working on {pic_list[pic_index]}: {pic_index+1} of {len(pic_list)}')
            img = matplotlib.image.imread(pic_list[pic_index])

            # Loop through images
            for index in range(len(image_coordinates)):
               # try:
                print(f'Working on {index+1} from {pic_list[pic_index]}')
                y1, y2, x1, x2 = image_coordinates[index]
                curr_img = img[y1:y2, x1:x2]
                curr_img = cv2.cvtColor(
                    curr_img, cv2.COLOR_BGR2RGB)
                _, mask = get_mask(img)
                # img[mask == 255] = [0, 255, 127]
                # mask = cv2.bitwise_not(mask)
                curr_img = rotate_image(
                    curr_img, image_coordinates[index])
                cv2.imwrite(os.path.join(self.output_folder, os.path.basename(
                    pic_list[pic_index]) + '_' + str(index+1) + '.png'), curr_img)
               # except Exception as e:
                #    print(
                #        f'Error with {index + 1} from {pic_list[pic_index]} : { e }')
                #    continue
