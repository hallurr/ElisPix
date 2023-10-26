# ElisPix

ElisPix is a Python project for processing images containing multiple smaller pictures. The project contains functions to crop, rotate, and perform other image processing operations to extract and correct individual pictures from the composite image.
---

## Dependencies

- NumPy
- Matplotlib
- OpenCV
- SciPy

### Installation of Dependencies

To install the required libraries, run the following commands:
```bash
pip install numpy
pip install matplotlib
pip install opencv-python
pip install scipy
```

## Installation Instructions

```bash
# Clone the repository
git clone https://github.com/yourusername/ElisPix.git

# Navigate to the project directory
cd ElisPix

# Install dependencies
pip install numpy matplotlib opencv-python scipy
```

## Usage
1. Store all your images in a folder, and update the picfoldername variable with the path to the folder.
2. Update the savefolder variable with the path to the folder where you want to save the processed images.
3. Run the second cell in the ipython notebook with VS Code.

## Functions
⋅⋅* crop_image: Crops the image based on provided coordinates.
⋅⋅* smearArray: Applies a smear effect to the image.
⋅⋅* rotate_image: Rotates the image by the given angle.
⋅⋅* findCutpoints: Finds the cut points for cropping.
⋅⋅* find_top_bottom_corners: Finds the top and bottom corners of an image.
⋅⋅* rotate_point: Rotates a point in the image.
⋅⋅* intricate_angle_finder: Finds the intricate angle for rotation.
⋅⋅* find_rotation_angle: Finds the rotation angle for an image.
⋅⋅* remove_white_border: Removes the white border from an image.

## Contribution
If you want to contribute to this project, feel free to fork the repository and submit a pull request.