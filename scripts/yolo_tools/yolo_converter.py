""" Convert origin ground truth files to yolo format """
import os
from PIL import Image

# global parameters needs to be modified for each task
IMG_FOLDER = './data/Images/001'  # origin image files folder
LABEL_FOLDER = './data/Labels/001'  # origin label files folder
YOLO_GT_FOLDER = './data/Yolo_gt/001'  # newly generated yolo ground truth directory
LABEL_NAMES = ['type_1', 'type_2', 'type_3', 'type_4', 'type_5', 'type_6']  # each label names in order
IMG_EXTENSION = 'bmp'  # extension of image files


def convert_label(name_):
    """ 
    Convert each label name listed in `LABEL_NAMES` as corresponding index.
    :param name_: real name for each labelled item
    """
    label = {k: i for i, k in enumerate(LABEL_NAMES)}
    return label[name_]


def convert_box(size, box):
    """ Bounding box format handler """
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
    """ Convert one item in original label file to yolo format"""
    box_item = item_list_.split()
    box_item[0] = convert_label(box_item[0])
    box_item[2], box_item[3] = box_item[3], box_item[2]  # Change the order to "xmin, xmax, ymin, ymax"
    box_item[1:] = convert_box(img_size_, list(map(lambda x: int(x), box_item[1:])))
    box_item = list(map(lambda x: str(x), box_item))
    return ' '.join(box_item)


def main():
    # create `YOLO_GT_FOLDER` if it's not existed
    if not os.path.isdir(YOLO_GT_FOLDER):
        os.makedirs(YOLO_GT_FOLDER)

    for img_file in os.listdir(IMG_FOLDER):
        # get image size
        with Image.open(os.path.join(IMG_FOLDER, img_file)) as img:
            img_size = img.size

        # open original label file and get objects count and information of each object
        with open(os.path.join(LABEL_FOLDER, img_file.replace(IMG_EXTENSION, 'txt'))) as gt_raw:
            cls_count = gt_raw.readline()
            item_list = list(map(lambda x: x.strip('\n'), gt_raw.readlines()))

        # write new yolo gt file
        with open(os.path.join(YOLO_GT_FOLDER, img_file.replace(IMG_EXTENSION, 'txt')), 'w') as gt_out:
            # check if label counts in the origin label file is correct or not
            if int(cls_count) == len(item_list):
                for item in item_list:
                    converted = gt_converter(item, img_size)
                    print('{}'.format(converted), file=gt_out)
            else:
                print("Mismatch label numbers found in file {}".format(img_file.replace(IMG_EXTENSION, 'txt')))
                continue


if __name__ == '__main__':
    main()
