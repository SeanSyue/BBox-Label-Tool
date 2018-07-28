from os import listdir
from os.path import join as joinpath
import re
from shutil import copyfile


PATH_NUM = '006'
SLICE_NUM = 120


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


if __name__ == '__main__':
    for item in sorted_alphanumeric(listdir(f'data/Labels/{PATH_NUM}'))[:SLICE_NUM]:
        with open(joinpath(f'./data/Labels/{PATH_NUM}', item)) as f:
            if f.readline().strip('\n') != '0':
                copyfile(joinpath(f'data/Images/{PATH_NUM}', item.replace('txt', 'bmp')),
                         joinpath('data/defect_yolo_center/JPEGImage', item.replace('txt', 'bmp')))
                copyfile(joinpath(f'data/Labels/{PATH_NUM}', item),
                         joinpath('data/defect_yolo_center/label', item))
