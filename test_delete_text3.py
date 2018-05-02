# -------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi
# Created:     06/06/2014
# -------------------------------------------------------------------------------
"""
Able to delete class label text
Record coordinates in top-left to buttom-down fashion
"""
from tkinter import *
from PIL import Image, ImageTk
import os
import glob

# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
IMG_FOLDER = './test/Images'
GT_FOLDER = './test/Labels'


class PopupWindow(object):
    def __init__(self, master):
        self.value = None
        self.top = Toplevel(master)
        self.label = Label(self.top, text="Input class")
        self.label.pack()
        self.entry = Entry(self.top)
        self.entry.pack()
        self.entry.focus_set()
        self.btn = Button(self.top, text='Ok', command=self.cleanup)
        self.btn.pack()

    def cleanup(self):
        self.value = self.entry.get()
        self.top.destroy()


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
        self.textIdList = []
        self.textId = None
        self.bboxList = []
        self.h_line = None
        self.v_line = None

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

        # popup window
        self.window = None
        self.is_pop = False

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)

    def loadDir(self, dbg=False):
        print("Load image. ")
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'

        # get image list
        self.imageDir = os.path.join(f'{IMG_FOLDER}', '%03d' % self.category)
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.JPEG'))
        if len(self.imageList) == 0:
            print("No .JPEG images found in the specified dir!")
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        # set up output dir
        self.outDir = os.path.join(f'{GT_FOLDER}', '%03d' % self.category)
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        self.loadImage()
        print(("%d images loaded from %s" % (self.total, s)))

    def loadImage(self):
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
                    if i == 0:
                        continue
                    tmp = [l.strip() for l in line.split(' ')]
                    # self.bboxList.append(tuple(tmp))
                    old_label = {'cls': tmp[0],
                                 'x1': min(int(tmp[1]), int(tmp[3])),
                                 'y1': min(int(tmp[2]), int(tmp[4])),
                                 'x2': max(int(tmp[1]), int(tmp[3])),
                                 'y2': max(int(tmp[2]), int(tmp[4]))}  # NEW
                    self.bboxList.append('{cls} {x1} {y1} {x2} {y2}'.format(**old_label))  # NEW
                    rect_id = self.mainPanel.create_rectangle(old_label['x1'], old_label['y1'],
                                                              old_label['x2'], old_label['y2'],
                                                              width=2,
                                                              outline=COLORS[(len(self.bboxList) - 1) % len(COLORS)])
                    text_id = self.mainPanel.create_text(old_label['x1'], old_label['y1'],
                                                         font="Times 20 italic bold",
                                                         text=old_label['cls'],
                                                         fill=COLORS[(len(self.bboxList) - 1) % len(COLORS)])

                    print(f"rect_id: {rect_id}; text_id: {text_id}  --  [loadImage]")
                    self.bboxIdList.append(rect_id)
                    # self.textIdList.append(text_id-1)
                    self.textIdList.append(text_id)
                    print(f"bboxIdList: {self.bboxIdList}; textIdList: {self.textIdList}  --  [loadImage]")
                    self.listbox.insert(END, '{cls}: ({x1}, {y1}) -> ({x2}, {y2})'.format(**old_label))  # NEW
                    self.listbox.itemconfig(len(self.bboxIdList) - 1,
                                            fg=COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
            if len(self.bboxIdList) != len(self.textIdList):
                print("[Warning]: Missing bounding box or class label detected!")

    def saveLabel(self):
        with open(self.labelfilename, 'w') as f:
            f.write('{}\n'.format(len(self.bboxList)))
            for bbox in self.bboxList:
                # f.write(' '.join(map(str, bbox)) + '\n')
                f.write('{}\n'.format(bbox))  # NEW
        print("------- Image No. {} saved -------".format(self.cur))

    def onMouseClick(self, event):
        print("[onMouseClick]")
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:  # self.STATE['click'] == 0:
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None

            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)

            self.startPopupWindow()
            cls = self.getInputClass()  # NEW

            new_label = {'cls': cls, 'x1': min(x1, x2), 'y1': min(y1, y2), 'x2': max(x1, x2), 'y2': max(y1, y2)}  # NEW
            self.bboxList.append('{cls} {x1} {y1} {x2} {y2}'.format(**new_label))  # NEW

            # print(f"bboxId: {self.bboxId}; textId: {self.textId}  --  [onMouseClick]")

            self.textId = self.mainPanel.create_text(new_label['x1'], new_label['y1'],
                                                     fill=COLORS[(len(self.bboxList) - 1) % len(COLORS)],
                                                     font="Times 20 italic bold",
                                                     text=cls)
            self.textIdList.append(self.textId)
            self.textId = None

            self.listbox.insert(END, '{cls}: ({x1}, {y1}) -> ({x2}, {y2})'.format(**new_label))  # NEW
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def onMouseMove(self, event):
        """Events when cursor is moving."""
        if self.is_pop is False:
            self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
            # If image is loaded, display coordinate auxiliary lines
            if self.tkimg:
                if self.h_line:
                    self.mainPanel.delete(self.h_line)
                self.h_line = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width=2)
                if self.v_line:
                    self.mainPanel.delete(self.v_line)
                self.v_line = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width=2)
            # Create temporary rectangle changing its shape while cursor is moving.
            if 1 == self.STATE['click']:
                if self.bboxId:
                    self.mainPanel.delete(self.bboxId)
                self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'],
                                                              event.x, event.y,
                                                              width=2,
                                                              outline=COLORS[len(self.bboxList) % len(COLORS)])
                # self.textId = self.bboxId+1

    def startPopupWindow(self):

        self.window = PopupWindow(self.parent)

        self.is_pop = True
        self.mainPanel.unbind('<Motion>')
        self.mainPanel.unbind('<Button-1>')
        self.ldBtn['state'] = 'disabled'
        self.btnDel['state'] = 'disabled'
        self.btnClear['state'] = 'disabled'
        self.prevBtn['state'] = 'disabled'
        self.nextBtn['state'] = 'disabled'
        self.goBtn['state'] = 'disabled'

        self.parent.wait_window(self.window.top)

        self.ldBtn['state'] = 'normal'
        self.btnDel['state'] = 'normal'
        self.btnClear['state'] = 'normal'
        self.prevBtn['state'] = 'normal'
        self.nextBtn['state'] = 'normal'
        self.goBtn['state'] = 'normal'
        self.mainPanel.bind('<Button-1>', self.onMouseClick)
        self.mainPanel.bind('<Motion>', self.onMouseMove)
        self.is_pop = False

    def getInputClass(self):
        return self.window.value

    def cancelBBox(self, *event):
        """Cancel ongoing process of drawing a bounding box."""
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def onClickDelBtn(self):
        print(f"========== [onClickDelBtn] ========== \n"
              f"bboxIdList: {self.bboxIdList}\n"
              f"textIdList: {self.textIdList}  -- [onClickDelBtn]")
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        print(f"idx: {idx}\n"
              f"bboxIdList: {self.bboxIdList}\n"
              f"textIdList: {self.textIdList}\n"
              f"bboxId: {self.bboxId}\n"
              f"textId: {self.textId}  -- [onClickDelBtn]")
        self.mainPanel.delete(self.bboxIdList[idx])  # NEW
        self.mainPanel.delete(self.textIdList[idx])
        self.bboxIdList.pop(idx)
        self.textIdList.pop(idx)  # NEW
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearAllBBox(self):
        print("[clearAllBBox]")
        for b_i in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[b_i])
        for t_i in range(len(self.textIdList)):  # NEW
            self.mainPanel.delete(self.textIdList[t_i])  # NEW
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.textIdList = []  # NEW
        self.bboxList = []

    def prevImage(self, *event):
        self.saveLabel()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, *event):
        self.saveLabel()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        # if 1 <= idx and idx <= self.total:
        if 1 <= idx <= self.total:
            self.saveLabel()
            self.cur = idx
            self.loadImage()
        self.label.focus_set()
        self.idxEntry.delete(0)


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width=True, height=True)
    root.mainloop()
