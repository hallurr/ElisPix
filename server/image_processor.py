import numpy as np
import cv2
from typing import List
from image_transformer import rotate_image
from image_utils import get_image_json, extract_subimage_by_coordinates, get_images_after_splitting
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self):
        self.results = []

    def process_images(self, image_files: List) -> List:
        for pic_index, pic in enumerate(image_files):
            logger.info(
                f'Working on {pic.filename}: {pic_index + 1} of {len(image_files)}')
            img = self.read_and_decode_image(pic)
            if img is not None:
                self.process_single_image(img, pic)
        return self.results

    def read_and_decode_image(self, pic) -> np.ndarray:
        try:
            npimg = np.frombuffer(pic.read(), np.uint8)
            img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f'Failed to read or decode {pic.filename}: {e}')
            return None

    def process_single_image(self, img: np.ndarray, pic) -> None:
        image_coordinates = get_images_after_splitting(img)
        for index, coordinates in enumerate(image_coordinates):
            try:
                curr_image = extract_subimage_by_coordinates(img, coordinates)
                curr_image = rotate_image(curr_image)
                self.results.append(get_image_json(curr_image))
            except Exception as e:
                logger.error(
                    f'Error processing {index + 1} from {pic.filename}: {e}')
