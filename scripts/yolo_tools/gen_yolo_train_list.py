"""
Generate list of absolute path to labelled images for yolo training.
Usage:
Rename the folder containing labelled images as 'JPEGImages'
and the corresponding label file folder as `labels`.
Put this script and two folders above under the same directory in a yolo training environment,
then run this script to generate training list.
"""
from pathlib import Path

for img_file in Path('/JPEGImages').iterdir():
    with open('defect_train.txt', 'w') as f:
<<<<<<< HEAD
        print(img_file.resolve(), file=f)
=======
        print(img_file.resolve(), file=f)
>>>>>>> 42f352feecc552d9cbecb13ae61854d85392ab77
