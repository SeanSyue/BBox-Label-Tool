import os
from PIL import Image
FILE = 'data/Labels/001/3.txt'

def convert_label(name_):
    label_ = {'motorbike': 0, 'bicycle': 1,
              'person': 2, 'truck': 3,
              'car': 4, 'bus': 5,
              'van': 6, 'others': 7}
    return label_[name_]


def convert_box(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return x, y, w, h


def gt_converter(item_list_, img_size_):
    box_item = item_list_.split()
    box_item[0] = convert_label(box_item[0])
    box_item[2], box_item[3] = box_item[3], box_item[2]  # Change the order to "xmin, xmax, ymin, ymax"
    box_item[1:] = convert_box(img_size_, list(map(lambda x: int(x), box_item[1:])))
    box_item = list(map(lambda x: str(x), box_item))
    return ' '.join(box_item)


for i in range(1, 172):
    with Image.open(f'data/Images/001/{i}.jpeg') as img:
        img_size = img.size

    with open(os.path.join('data/Yolo_gt/001', '{}.txt'.format(i)), 'w') as out:
        with open(f'data/Labels/001/{i}.txt') as raw:
            cls_count = raw.readline()
            item_list = list(map(lambda x: x.strip('\n'), raw.readlines()))
            if int(cls_count) == len(item_list):
                for item in item_list:
                    converted = gt_converter(item, img_size)
                    print('{}'.format(converted), file=out)
            else:
                print(f"Mismatch label numbers found in file {i}.txt")
                continue
