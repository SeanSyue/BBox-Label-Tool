import os


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


def convert_label(name_):
    label_ = {'motorbike': 0, 'bicycle': 1,
              'person': 2, 'truck': 3,
              'car': 4, 'bus': 5,
              'van': 6, 'others': 7}
    return label_[name_]


def gt_generator(origin_file):
    with open(origin_file) as xml:
        root = ET.parse(xml).getroot()
        size = root.find('size')

        img_size = (int(size.find('width').text), int(size.find('height').text))

        for obj in root.iter('object'):
            label_ = convert_label(obj.find('name').text)

            bndbox = obj.find('bndbox')
            box_origin = (float(bndbox.find('xmin').text),
                          float(bndbox.find('xmax').text),
                          float(bndbox.find('ymin').text),
                          float(bndbox.find('ymax').text))
            new_x, new_y, new_w, new_h = convert_box(img_size, box_origin)
            yield '{} {} {} {} {}'.format(label_, new_x, new_y, new_w, new_h)


os.chdir('data/test')
XML_DIR = 'XML'
IMG_DIR = 'img'
for i in range(50):
    with open(os.path.join(IMG_DIR, '{}.txt'.format(i)), 'w') as f:
        for line in gt_generator(os.path.join(XML_DIR, '{}.xml'.format(i))):
            print(line, file=f)
