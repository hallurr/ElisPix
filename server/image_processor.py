import numpy as np
import cv2
from typing import List
from image_utils import get_image_json, get_images_after_splitting, extract_subimage_by_coordinates, read_and_decode_image
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self):
        self.results = []

    def process_images(self, image_files: List) -> List:
        for scanned_image_index, scanned_image in enumerate(image_files):
            logger.info(
                f'Working on {scanned_image.filename}: {scanned_image_index + 1} of {len(image_files)}')
            try:
                scanned_image_np = read_and_decode_image(scanned_image)
                if scanned_image_np is not None:
                    self.process_single_image(
                        scanned_image_np, scanned_image.filename)
            except Exception as e:
                logger.error(
                    f'Failed to read or decode {scanned_image.filename}: {e}')
        return self.results

    def process_single_image(self, scanned_image_np: np.ndarray, filename) -> None:
        image_coordinates = get_images_after_splitting(scanned_image_np)
        for index, coordinates in enumerate(image_coordinates):
            try:
                curr_image = extract_subimage_by_coordinates(
                    scanned_image_np, coordinates)
                self.results.append(get_image_json(curr_image))
            except Exception as e:
                logger.error(
                    f'Error processing {index + 1} from {filename}: {e}')
