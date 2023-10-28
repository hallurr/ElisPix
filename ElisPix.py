import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
import tkinter as tk
# from tkinter import filedialog
from ImageProcessor import ImageProcessor
import warnings


def submit():
    image_processor = ImageProcessor('inputfolder', 'outputfolder')
    image_processor.process_images()


if __name__ == "__main__":
    warnings.filterwarnings('ignore')  # Suppress warnings

    root = tk.Tk()
    root.title("ElisPix")

    # Input Path
    """     frame_input = tk.Frame(root)
    frame_input.pack(pady=5, fill='x', padx=5)
    tk.Label(frame_input, text="Input folder:").pack(side='left', padx=5)
    input_path_var = tk.StringVar()
    input_path_entry = tk.Entry(
        frame_input, textvariable=input_path_var, width=50)
    input_path_entry.pack(side='left', expand=True, fill='x')
    tk.Button(frame_input, text="Browse", command=lambda: input_path_var.set(
        filedialog.askdirectory())).pack(side='left', padx=5)
    """
    # Output Path
    """ frame_output = tk.Frame(root)
    frame_output.pack(pady=5, fill='x', padx=5)
    tk.Label(frame_output, text="Output folder:").pack(side='left', padx=5)
    output_path_var = tk.StringVar()
    output_path_entry = tk.Entry(
        frame_output, textvariable=output_path_var, width=50)
    output_path_entry.pack(side='left', expand=True, fill='x')
    tk.Button(frame_output, text="Browse", command=lambda: output_path_var.set(
        filedialog.askdirectory())).pack(side='left', padx=5) """

    # Output File Type
    """ frame_file_type = tk.Frame(root)
    frame_file_type.pack(pady=5, fill='x', padx=5)
    tk.Label(frame_file_type, text="Output file type:").pack(
        side='left', padx=5)
    file_type_var = tk.StringVar(root)
    file_type_var.set('jpg')  # Set default value
    file_type_menu = tk.OptionMenu(
        frame_file_type, file_type_var, 'jpg', 'png', 'tif')
    file_type_menu.pack(side='left', padx=5) """

    # Submit Button
    tk.Button(root, text="Start Processing", command=submit).pack(pady=20)

    root.mainloop()
