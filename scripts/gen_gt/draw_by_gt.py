""" Draw bounding boxes corresponds to ground truth files """
import os
from PIL import Image, ImageDraw

os.chdir('./data/defect_yolo_center')

SRC_IMG_PATH = './JPEGImages_origin_name'
LABEL_PATH = './label_raw'
OUT_PATH = './img_box'


if not os.path.isdir(OUT_PATH):
    os.makedirs(OUT_PATH)

for img_file in os.listdir(SRC_IMG_PATH):
    img = Image.open(f'{SRC_IMG_PATH}/{img_file}')
    
    draw = ImageDraw.Draw(img)
    with open(f'{LABEL_PATH}/{img_file.replace("bmp", "txt")}') as f:
        label = f.readlines()[-1].strip('\n').split(' ')
    draw.rectangle(((int(label[1]), int(label[2])), (int(label[3]), int(label[4]))), outline='red')
    
    img.save(f'{OUT_PATH}/{img_file.replace("bmp", "jpg")}', 'JPEG')
