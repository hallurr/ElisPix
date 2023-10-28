import numpy as np
import matplotlib.image
import matplotlib.pyplot
import cv2
import os
from scipy import ndimage
import pathlib
import tkinter as tk
# from tkinter import filedialog


def find_cutpoints(thresh, thresholddivider=200, percent_smear=0.00125, row_or_col='row'):
    picstarts = []
    picends = []
    if row_or_col == 'row':
        # print('row')
        rowsum = np.sum(thresh, axis=1)
    else:
        rowsum = np.sum(thresh, axis=0)
        # print('col')
    rowsum = smear_array(rowsum, percent_smear)
    rowsum_orig = rowsum
    thresholdvalue = np.mean(rowsum)/thresholddivider
    loopflag = True
    matplotlib.pyplot.close()
    matplotlib.pyplot.figure()
    cutvalue = 0
    while loopflag:
        # check if rowsum is all zeros or all nonzeros
        if np.all(rowsum > thresholdvalue) or np.all(rowsum < thresholdvalue):
            loopflag = False
        else:
            # check if there are any non zeros in the rowsum array
            if np.any(rowsum > thresholdvalue):
                picstarts.append(
                    np.argmax(rowsum > thresholdvalue)+cutvalue)
                rowsum = rowsum[np.argmax(rowsum > thresholdvalue):]
                cutvalue = picstarts[-1]
            if np.any(rowsum < thresholdvalue):
                picends.append(np.argmax(rowsum < thresholdvalue)+cutvalue)
                rowsum = rowsum[np.argmax(rowsum < thresholdvalue):]
                cutvalue = picends[-1]

    return picstarts, picends, rowsum_orig


def smear_array(rowsum, percentsmear=0.00125):
    smearedrowsum = np.zeros(len(rowsum))
    smearlength = int(len(rowsum) * percentsmear)
    temprowsum = np.zeros(len(rowsum)+2*smearlength)
    temprowsum[smearlength:-smearlength] = rowsum
    # print(len(smearedrowsum))
    for i in range(smearlength):
        smearedrowsum = smearedrowsum + \
            temprowsum[i:i+len(rowsum)] / (smearlength*2)
        # Now the other side
        smearedrowsum = smearedrowsum + \
            temprowsum[-i-len(rowsum)-1:-i-1] / (smearlength*2)
    return smearedrowsum


def crop_image(img, x1, y1, x2, y2):
    # Ensure coordinates are within bounds
    h, w = img.shape[:2]
    x1, y1 = max(0, int(x1)), max(0, int(y1))
    x2, y2 = min(w, int(x2)), min(h, int(y2))

    # Crop the image
    cropped_img = img[y1:y2, x1:x2]
    return cropped_img


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(
        image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def find_top_bottom_corners(thresh):
    # Find all non-zero pixel coordinates
    non_zero_y, non_zero_x = np.where(thresh > 0)

    # Find top corner (minimum y-coordinate)
    top_idx = np.argmin(non_zero_y)
    top_corner = (non_zero_x[top_idx], non_zero_y[top_idx])

    # Find bottom corner (maximum y-coordinate)
    bottom_idx = np.argmax(non_zero_y)
    bottom_corner = (non_zero_x[bottom_idx], non_zero_y[bottom_idx])

    return top_corner, bottom_corner


def rotate_point(x, y, height, width, angle):
    # Convert angle to radians
    angle_rad = np.deg2rad(angle)

    # Define rotation matrix
    rotation_matrix = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad)],
        [np.sin(angle_rad), np.cos(angle_rad)]
    ])

    # Subtract the center of the image
    x_centered = x - width / 2
    y_centered = y - height / 2

    # Apply the rotation
    new_x_centered, new_y_centered = np.dot(
        rotation_matrix, [x_centered, y_centered])

    # Add back the center of the image
    new_x = new_x_centered + width / 2
    new_y = new_y_centered + height / 2

    return new_x, new_y


def find_rotation_angle(curr_thresh, startpercent=0.8, awaydistance=0.025, enddistance=0.075, skips=5):
    ylength = curr_thresh.shape[0]

    # # Choose starting % from top
    # startpercent = 0.8
    # # choose starting distance from startpercent from top
    # awaydistance = 0.025
    # # choose ending distance from startpercent
    # enddistance = 0.075
    # # choose how many points to skip
    # skips = 5

    ystart = int(ylength * startpercent)
    yupstart = int(ylength * (startpercent - awaydistance))
    yupend = int(ylength * (startpercent - awaydistance - enddistance))
    up_mean = (yupend+yupstart)/2
    ydownstart = int(ylength * (startpercent + awaydistance))
    ydownend = int(ylength * (startpercent + awaydistance + enddistance))
    down_mean = (ydownstart+ydownend)/2

    row_indices_25 = np.arange(yupend, yupstart, skips)
    first_white_pixels_25 = np.argmax(
        curr_thresh[row_indices_25, :], axis=1)
    mean_x25 = np.mean(first_white_pixels_25)

    row_indices_75 = np.arange(ydownstart, ydownend, skips)
    first_white_pixels_75 = np.argmax(
        curr_thresh[row_indices_75, :], axis=1)
    mean_x75 = np.mean(first_white_pixels_75)

    # find the slope of the line between the two points
    slope = (mean_x75 - mean_x25) / (down_mean - up_mean)

    # find the angle of the line
    angle = np.arctan(slope) * 180 / np.pi

    return angle


def intricate_angle_finder(curr_thresh):
    angles = []
    # flip curr_thresh left to right
    curr_threshflipped = np.fliplr(curr_thresh)
    # flip curr_thresh up and down
    curr_threshflipped = np.flipud(curr_threshflipped)
    for i in range(10, 90, 1):
        n = i/100
        try:
            angles.append(find_rotation_angle(
                curr_thresh, startpercent=n, awaydistance=0.05, enddistance=0.05, skips=2))
            angles.append(find_rotation_angle(
                curr_threshflipped, startpercent=n, awaydistance=0.05, enddistance=0.05, skips=2))
        except:
            continue
    return np.median(angles), angles


def remove_white_border(input_image):
    # Convert image to grayscale
    input_grayscale = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to create a mask of the non-white pixels
    _, thresh3 = cv2.threshold(
        input_grayscale, 250, 255, cv2.THRESH_BINARY_INV)

    threshold_divider = 200
    percent_smear = 0.005

    # find cutpoints rowwise
    _, _, rowsum = find_cutpoints(
        thresh3, threshold_divider, percent_smear, 'row')
    _, _, colsum = find_cutpoints(
        thresh3, threshold_divider, percent_smear, 'col')

    row_threshold = np.mean(rowsum)
    col_threshold = np.mean(colsum)

    startofimg = np.where(rowsum > row_threshold)[0][0]
    endofimg = np.where(rowsum > row_threshold)[0][-1]
    startofimgside = np.where(colsum > col_threshold)[0][0]
    endofimgside = np.where(colsum > col_threshold)[0][-1]
    return startofimg, endofimg, startofimgside, endofimgside


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
        # List all files in folder
        pic_list = list(pathlib.Path(self.input_folder).glob('*.tif'))

        # Loop through all the megaimages to find the subimages
        for pic_index in range(len(pic_list)):
            print(
                f'Working on {pic_list[pic_index]}: {pic_index+1} of {len(pic_list)}')

            # Read in current pic as array
            img = matplotlib.image.imread(pic_list[pic_index])

            # Change to grayscale and apply threshold
            image_grayscale = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            ret, thresh = cv2.threshold(
                image_grayscale, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Find row cutpoints
            threshold_divider = 200
            percent_smear = 0.00125
            start_row, end_row, _ = find_cutpoints(
                thresh, threshold_divider, percent_smear, 'row')

            # Adjust such that we have the same number of starts and ends and that the first value is a start
            if start_row[0] > end_row[0]:
                start_row = [0] + start_row
            if end_row[-1] < start_row[-1]:
                end_row = end_row + [thresh.shape[0]]

            image_orientation = dict()  # dictionary to save the image orientation of the pictures
            image_coordinates = dict()  # dictionary to save the image coordinates of the pictures

            # Loop through all starts and ends and save the image
            for i in range(len(start_row)):
                # Find column cutpoints
                start_col, end_col, _ = find_cutpoints(
                    thresh[start_row[i]:end_row[i], :], threshold_divider, percent_smear, 'col')
                # Adjust such that we have the same number of starts and ends and that the first value is a start
                if start_col[0] > end_col[0]:
                    start_col = [0] + start_col
                if end_col[-1] < start_col[-1]:
                    end_col = end_col + [thresh.shape[1]]
                # Loop through all starts and ends and save the image
                for j in range(len(start_col)):
                    image_coordinates[f'Img_row{int(i+1)}_col{int(j+1)}'] = [
                        start_row[i], end_row[i], start_col[j], end_col[j]]
                    # Save if the image top corner is on the left or right side
                    image_orientation[f'Img_row{int(i+1)}_col{int(j+1)}'] = 'left' if start_col[j] < thresh.shape[1]/2 else 'right'

            print(
                f'Found {len(image_coordinates)} images in {pic_list[pic_index]}')

            # Loop through all images in the megaimage and save them
            for i in range(len(image_coordinates)):
                try:
                    curr_key = list(image_coordinates.keys())[i]
                    print(f'Working on {curr_key} from {pic_list[pic_index]}')
                    curr_img = img[image_coordinates[curr_key][0]:image_coordinates[curr_key]
                                   [1], image_coordinates[curr_key][2]:image_coordinates[curr_key][3]]
                    curr_thresh = thresh[image_coordinates[curr_key][0]:image_coordinates[curr_key]
                                         [1], image_coordinates[curr_key][2]:image_coordinates[curr_key][3]]

                    # To find the rotation angle we find the slope of the line between two x,y points
                    angle, _ = intricate_angle_finder(curr_thresh)

                    # Find the corners before rotation
                    fixsmear = int(percent_smear/2)
                    if image_orientation[curr_key] == 'left':
                        x_top, y_top = fixsmear, fixsmear
                        x_bottom, y_bottom = curr_thresh.shape[1] - \
                            fixsmear, curr_thresh.shape[0]-fixsmear
                    else:
                        x_top, y_top = curr_thresh.shape[1]-fixsmear, fixsmear
                        x_bottom, y_bottom = fixsmear, curr_thresh.shape[0]-fixsmear

                    # Rotate the image
                    curr_img = cv2.bitwise_not(curr_img)
                    rotated_img = ndimage.rotate(curr_img, -angle)

                    # Invert curr_img such that black is white and white is black
                    rotated_img = cv2.bitwise_not(rotated_img)
                    curr_img = cv2.cvtColor(rotated_img, cv2.COLOR_BGR2RGB)

                    # Rotate clockwise by 90 degrees & remove white border
                    curr_img = cv2.rotate(curr_img, cv2.ROTATE_90_CLOCKWISE)
                    startofimg, endofimg, startofimgside, endofimgside = remove_white_border(
                        curr_img)
                    curr_img = curr_img[startofimg:endofimg,
                                        startofimgside:endofimgside]

                    # Save image
                    cv2.imwrite(os.path.join(self.output_folder, os.path.basename(
                        pic_list[pic_index]) + '_' + curr_key + '.tif'), curr_img)
                except Exception as e:
                    print(
                        f'Error with {curr_key} from {pic_list[pic_index]} : { e }')
                    continue
