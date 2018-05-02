# -------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi
# Created:     06/06/2014
# -------------------------------------------------------------------------------

from tkinter import *
from PIL import Image, ImageTk
import os
import glob

# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']


class LabelTool:
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=FALSE, height=FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = dict()
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text="Image Dir:")
        self.label.grid(row=0, column=0, sticky=E)
        self.entry = Entry(self.frame)
        self.entry.grid(row=0, column=1, sticky=W + E)
        self.entry.focus_set()
        self.ldBtn = Button(self.frame, text="Load", command=self.loadDir)
        self.ldBtn.grid(row=0, column=2, sticky=W + E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind('<Button-1>', self.onMouseClick)
        self.mainPanel.bind('<Motion>', self.onMouseMove)
        self.parent.bind('<Escape>', self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind('s', self.cancelBBox)
        self.parent.bind('a', self.prevImage)  # press 'a' to go backforward
        self.parent.bind('d', self.nextImage)  # press 'd' to go forward
        self.mainPanel.grid(row=1, column=1, rowspan=4, sticky=W + N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text='Bounding boxes:')
        self.lb1.grid(row=1, column=2, sticky=W + N)
        self.listbox = Listbox(self.frame, width=22, height=12)
        self.listbox.grid(row=2, column=2, sticky=N)
        self.btnDel = Button(self.frame, text='Delete', command=self.onClickDelBtn)
        self.btnDel.grid(row=3, column=2, sticky=W + E + N)
        self.btnClear = Button(self.frame, text='ClearAll', command=self.clearAllBBox)
        self.btnClear.grid(row=4, column=2, sticky=W + E + N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=5, column=1, columnspan=2, sticky=W + E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width=10, command=self.prevImage)
        self.prevBtn.pack(side=LEFT, padx=5, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width=10, command=self.nextImage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=LEFT, padx=5)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image No.")
        self.tmpLabel.pack(side=LEFT, padx=5)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoImage)
        self.goBtn.pack(side=LEFT)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side=RIGHT)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)

    def loadDir(self, dbg=False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'

        # get image list
        self.imageDir = os.path.join(r'./test/Images', '%03d' % self.category)
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.JPEG'))
        if len(self.imageList) == 0:
            print("No .JPEG images found in the specified dir!")
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        # set up output dir
        self.outDir = os.path.join(r'./test/Labels', '%03d' % self.category)
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        self.loadImage()
        print(("%d images loaded from %s" % (self.total, s)))

    def loadImage(self):
        print("== loadImage ==")
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width=max(self.tkimg.width(), 400), height=max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.progLabel.config(text='%04d/%04d' % (self.cur, self.total))

        # load labels
        self.clearAllBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    print("i: {}, line: {}".format(i, line))
                    if i == 0:
                        continue
                    tmp = [l.strip() for l in line.split(' ')]
                    print("tmp: {}  -- loadImage".format(tmp))
                    # self.bboxList.append(tuple(tmp))
                    old_label = {'cls': tmp[0], 'x1': int(tmp[1]), 'y1': int(tmp[2]),
                                 'x2': int(tmp[3]), 'y2': int(tmp[4])}  # NEW
                    self.bboxList.append('{cls} {x1} {y1} {x2} {y2}'.format(**old_label))  # NEW
                    # tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1],
                    #                                         tmp[2], tmp[3],
                    #                                         width=2,
                    #                                         outline=COLORS[(len(self.bboxList) - 1) % len(COLORS)])
                    tmpId = self.mainPanel.create_rectangle(old_label['x1'], old_label['y1'],  # NEW
                                                            old_label['x2'], old_label['y2'],
                                                            width=2,
                                                            outline=COLORS[(len(self.bboxList) - 1) % len(COLORS)])
                    self.mainPanel.create_text(old_label['x1'], old_label['y1'],
                                               fill=COLORS[(len(self.bboxList) - 1) % len(COLORS)],
                                               font="Times 20 italic bold",
                                               text=old_label['cls'])

                    self.bboxIdList.append(tmpId)
                    # self.listbox.insert(END, '(%d, %d) -> (%d, %d)' % (tmp[0], tmp[1], tmp[2], tmp[3]))
                    self.listbox.insert(END, '{cls}: ({x1}, {y1}) -> ({x2}, {y2})'.format(**old_label))  # NEW
                    self.listbox.itemconfig(len(self.bboxIdList) - 1,
                                            fg=COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveLabel(self):
        print("== saveLabel ==")
        with open(self.labelfilename, 'w') as f:
            f.write('{}\n'.format(len(self.bboxList)))
            for bbox in self.bboxList:
                # f.write(' '.join(map(str, bbox)) + '\n')
                print("bbox type: {}  --  func saveLabel".format(type(bbox)))
                print("bbox: {}  --  func saveLabel".format(bbox))
                f.write('{}\n'.format(bbox))  # NEW
        print("Image No. {} saved".format(self.cur))

    def onMouseClick(self, event):
        print("== onMouseClick ==")
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            cls = 'class'  # NEW
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            new_label = {'cls': cls, 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}  # NEW
            print("{} -- from func onMouseClick". format(new_label))
            self.bboxList.append('{cls} {x1} {y1} {x2} {y2}'.format(**new_label))  # NEW
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            # self.listbox.insert(END, '(%d, %d) -> (%d, %d)' % (x1, y1, x2, y2))
            self.listbox.insert(END, '{cls}: ({x1}, {y1}) -> ({x2}, {y2})'.format(**new_label))  # NEW
            self.mainPanel.create_text(new_label['x1'], new_label['y1'],
                                       fill=COLORS[(len(self.bboxList) - 1) % len(COLORS)],
                                       font="Times 20 italic bold",
                                       text=cls)
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def onMouseMove(self, event):
        """Events when cursor is moving."""
        self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
        # If image is loaded, display coordinate auxiliary lines
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width=2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width=2)
        # Create temporary rectangle changing its shape while cursor is moving.
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'],
                                                          event.x, event.y,
                                                          width=2,
                                                          outline=COLORS[len(self.bboxList) % len(COLORS)])



    def cancelBBox(self, event):
        print("== cancelBBox ==")
        """Cancel ongoing process of drawing a bounding box."""
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def onClickDelBtn(self, event):
        print("== onClickDelBtn ==")
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearAllBBox(self):
        print("== clearAllBBox ==")
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []

    def prevImage(self, event):
        print("== prevImage ==")
        self.saveLabel()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event):
        print("== nextImage ==")
        self.saveLabel()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self, event):
        print("== gotoImage ==")
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveLabel()
            self.cur = idx
            self.loadImage()


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width=True, height=True)
    root.mainloop()
