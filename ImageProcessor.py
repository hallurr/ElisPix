import numpy as np
import matplotlib.image
import matplotlib.pyplot
import cv2
import os
import pathlib

LOWER_WHITE = np.array([200, 200, 200])
UPPER_WHITE = np.array([255, 255, 255])
NEON_GREEN = np.array([0, 255, 127])
PAD_RATIO = 0.1
MIN_OBJECT_RATIO = 0.1


def get_bounding_box(cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    return cv2.boundingRect(np.int0(box))


def get_mask(img):
    mask = cv2.inRange(img, LOWER_WHITE, UPPER_WHITE)
    mask = cv2.bitwise_not(mask)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_width = MIN_OBJECT_RATIO * img.shape[1]
    filtered_contours = [cnt for cnt in contours if cv2.boundingRect(cnt)[
        2] >= min_width]
    mask = np.zeros_like(mask)
    cv2.drawContours(mask, filtered_contours, -1, (255), thickness=cv2.FILLED)
    mask = cv2.bitwise_not(mask)
    return filtered_contours, mask


def add_border(img, pad_height, pad_width):
    return cv2.copyMakeBorder(img, pad_height, pad_height, pad_width, pad_width, cv2.BORDER_CONSTANT, value=[255, 255, 255])


def create_rectangle(cnt):
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    return cv2.boundingRect(np.int0(box))


def get_split_images(img):
    height, width, _ = img.shape
    pad_height = int(height * PAD_RATIO)
    pad_width = int(width * PAD_RATIO)
    img = add_border(img, pad_height, pad_width)
    contours, _ = get_mask(img)

    rectangles = [cnt for cnt in contours if create_rectangle(
        cnt)[2] >= width * MIN_OBJECT_RATIO and create_rectangle(cnt)[3] >= height * MIN_OBJECT_RATIO]

    rectangle_coordinates = [(y - pad_height, y - pad_height + h, x - pad_width,
                              x - pad_width + w) for x, y, w, h in map(create_rectangle, rectangles)]

    return rectangle_coordinates


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
        image, rotation_mat, (bound_w, bound_h), borderValue=([255, 255, 255]))
    return rotated_image


class ImageProcessor:
    def __init__(self, input_folder, output_folder):
        self.input_folder = pathlib.Path(input_folder)
        self.output_folder = pathlib.Path(output_folder)
        self.initialize_folders()

    def initialize_folders(self):
        self.input_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def process_images(self):
        pic_list = list(self.input_folder.glob('*.tif'))
        for pic_index, pic in enumerate(pic_list):
            img = cv2.imread(str(pic))
            image_coordinates = get_split_images(img)
            print(f'Working on {pic}: {pic_index+1} of {len(pic_list)}')
            img = matplotlib.image.imread(pic)

            # Loop through images
            for index, coordinates in enumerate(image_coordinates):
                try:
                    print(f'Working on {index+1} from {pic}')
                    y1, y2, x1, x2 = coordinates
                    curr_img = cv2.cvtColor(
                        img[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
                    filtered_contours, _ = get_mask(curr_img)
                    # for contour in filtered_contours:
                    #     x, y, w, h = cv2.boundingRect(contour)
                    #     cv2.rectangle(curr_img, (x, y),
                    #                   (x + w, y + h), (0, 255, 0), 10)
                    # curr_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                    cv2.imwrite(str(self.output_folder /
                                f'{pic.stem}_{index+1}.png'), curr_img)
                except Exception as e:
                    print(f'Error with {index + 1} from {pic} : { e }')
                    continue
