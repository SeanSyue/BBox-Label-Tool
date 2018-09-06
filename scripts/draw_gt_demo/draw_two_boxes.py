<<<<<<< HEAD
""" Draw two concentric rectangles by scratch """
import os
from PIL import Image, ImageDraw


NUM = 6
SRC_IMG_PATH = f'../../Lab_files/Defects_Type1_6/Type_{NUM}/defect'
LABEL_PATH = './data/defect_yolo_center/label_raw'
OUT_PATH = f'./data/defect_yolo_center/double_box_{NUM}'
MIDDLE = 130
SCALE_1 = 30
SCALE_2 = 15
=======
""" Draw bounding boxes corresponds to ground truth files """
import os
from PIL import Image, ImageDraw

os.chdir('./data/defect_yolo_center')

SRC_IMG_PATH = './JPEGImages_origin_name'
LABEL_PATH = './label_raw'
OUT_PATH = './img_box'
>>>>>>> 42f352feecc552d9cbecb13ae61854d85392ab77


if not os.path.isdir(OUT_PATH):
    os.makedirs(OUT_PATH)

<<<<<<< HEAD
for img_file in (item for item in os.listdir(SRC_IMG_PATH) if item != '.DS_Store'):
    img = Image.open(f'{SRC_IMG_PATH}/{img_file}')

    draw = ImageDraw.Draw(img)

    draw.rectangle(((MIDDLE-SCALE_1, MIDDLE-SCALE_1), (MIDDLE+SCALE_1, MIDDLE+SCALE_1)), outline='red')
    draw.rectangle(((MIDDLE-SCALE_2, MIDDLE-SCALE_2), (MIDDLE+SCALE_2, MIDDLE+SCALE_2)), outline='red')

=======
for img_file in os.listdir(SRC_IMG_PATH):
    img = Image.open(f'{SRC_IMG_PATH}/{img_file}')
    
    draw = ImageDraw.Draw(img)
    with open(f'{LABEL_PATH}/{img_file.replace("bmp", "txt")}') as f:
        label = f.readlines()[-1].strip('\n').split(' ')
    draw.rectangle(((int(label[1]), int(label[2])), (int(label[3]), int(label[4]))), outline='red')
    
>>>>>>> 42f352feecc552d9cbecb13ae61854d85392ab77
    img.save(f'{OUT_PATH}/{img_file.replace("bmp", "jpg")}', 'JPEG')
