# Custom multi-label labelling tool-kit (with yolo format transformer). 
## Output format: 
Text file (.txt), which name is identical to the target image, recode labelling infromation in the following format: 
```
OBJECT_COUNTS
CLASS_NAME_1 X1_MIN Y1_MIN X1_MAX Y1_MAX
CLASS_NAME_2 X2_MIN Y2_MIN X2_MAX Y2_MAX
......
```
* The first line shows total object counts in the image. 
* The folloing lines indicates one object recorded, with class name and the coordination of top-left point and bottom-right point
of bounding box. 

## Preparation: 
1. Create folder `data`;
2. In the folder `data`, create two more folders, named as `Images` and `Labels` respectively. 
3. Put all your images in one folder, name this folder as `001` and put it in the `Images` folder;
4. For more images folders, name them as `002`, `003`... and so on. The final structure in the `data` folder is something 
look like this: 
```
.
├── Images
│   ├── 001
│   │   ├── img_1.jpeg
│   │   ├── img_2.jpeg
│   │   └── img_3.jpeg
│   ├── 002
│   └── 003
└── Labes
```
5. Change the `IMG_EXTENSION` in file `main_labelling.py` to fit the format of your images; 
6. Change `CLASS_DICT` in the file `main_labelling.py` to the format below:
```
{"CODE_1": CLASS_NAME_1, "CODE_2": CLASS_NAME_2} 
```

## Labelling:
1. Input the number for image directory. For example, input `1` for `data/Images/001`; 
2. Click two points one by one to draw a rectangle of the region you wanna labelling; 
3. Key in the label codes (the thing you assigned in step 5 of preparation procedure)in the popup window. 

## Navigation:
1. Press key "x" or "z" (case insensitive) to navigate to next or previous page respectively. You can also press the 
button "Next >>" or "<< Prev" to do the same task. 
2. Key in the page number in the button next to the "Go to Image No." text and press "Go" button to let you jump to the 
page you wish. You can Press key  "g" (case insensitive) to set focus on the input box. 

## Ground truth conversion: 
Do the following steps to transform your label file. 
1. Create folder named `Yolo_gt` in the `data` folder;
2. run the `yolo_converter.py` script. 


