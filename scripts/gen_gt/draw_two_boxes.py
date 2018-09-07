""" Draw two concentric rectangles from scratch """
import os
from PIL import Image, ImageDraw


NUM = 6
SRC_IMG_PATH = f'../../Lab_files/Defects_Type1_6/Type_{NUM}/defect'
LABEL_PATH = './data/defect_yolo_center/label_raw'
OUT_PATH = f'./data/defect_yolo_center/double_box_{NUM}'
MIDDLE = 130
SCALE_1 = 30
SCALE_2 = 15


for img_file in (item for item in os.listdir(SRC_IMG_PATH) if item != '.DS_Store'):
    img = Image.open(f'{SRC_IMG_PATH}/{img_file}')

    draw = ImageDraw.Draw(img)

    draw.rectangle(((MIDDLE-SCALE_1, MIDDLE-SCALE_1), (MIDDLE+SCALE_1, MIDDLE+SCALE_1)), outline='red')
    draw.rectangle(((MIDDLE-SCALE_2, MIDDLE-SCALE_2), (MIDDLE+SCALE_2, MIDDLE+SCALE_2)), outline='red')

    img.save(f'{OUT_PATH}/{img_file.replace("bmp", "jpg")}', 'JPEG')
