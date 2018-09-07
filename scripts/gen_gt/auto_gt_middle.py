"""
Auto generate ground-truth files with one bounding box at the middle of the image.
Modify param `OFFSET` to change the generated bounding boxes size.
"""
from pathlib import Path
from PIL import Image

OFFSET = 30  # distance between the boundary of the bounding box and the center of the bounding box
IMG_EXTENSION = 'bmp'
CLASS_NAME = 'type_6'
PATH_NUM = '006'

if __name__ == '__main__':
    # loop over images
    for img_file in Path(f'./data/Images/{PATH_NUM}').glob(f'*.{IMG_EXTENSION}'):
        # get image size
        width, height = Image.open(img_file).size

        # calculate bounding box coordinate
        xmin = width // 2 - OFFSET
        ymin = height // 2 - OFFSET
        xmax = width // 2 + OFFSET
        ymax = height // 2 + OFFSET

        # auto generate ground truth
        with open(Path(f'./data/Labels/{PATH_NUM}').joinpath(img_file.stem + '.txt'), 'w') as f:
            print(f"1\n"
                  f"{' '.join((CLASS_NAME, str(xmin), str(ymin), str(xmax), str(ymax)))}",
                  file=f)
