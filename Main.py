from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from SazParser import processFiddler


class Root(Tk):

    def __init__(self):
        super(Root, self).__init__()
        self.title("Read fiddler")
        self.minsize(400, 200)
        # self.wm_iconbitmap('')

        self.labelFrame = ttk.LabelFrame(self, text="Open Fiddler")
        self.labelFrame.grid(column=0, row=1)
        self.button()

        self.isCommentedVar = IntVar()
        self.checkbox = ttk.Checkbutton(
            self, text="Commented", variable=self.isCommentedVar)
        self.checkbox.grid(column=0, row=3, sticky=W)

        self.timelabel = Label(self, text="Time(s)")
        self.timelabel.grid(column=0, row=2, sticky=W)

        self.timetext = Entry(self)
        self.timetext.grid(column=1, row=2, sticky=W)

        self.processBtn = ttk.Button(
            self, text="Process", command=self.process)
        self.processBtn.grid(column=0, row=5, columnspan=3, sticky=E)

    def button(self):
        self.button = ttk.Button(
            self.labelFrame, text="Browse", command=self.fileDialog)
        self.button.grid(column=0, row=1, sticky=W)

    def fileDialog(self):
        self.filename = filedialog.askopenfilename(
            initialdir="/", title="Select file",
            filetypes=(("saz files", "*.saz"), ("all files", "*.*")))

        self.selectedFile = Label(self.labelFrame, text="")
        self.selectedFile.grid(column=0, row=2)
        self.selectedFile.configure(text=self.filename)

    def process(self):
        print(self.isCommentedVar.get())
        processFiddler(self.filename, self.isCommentedVar.get(),
                       self.timetext.get())


if __name__ == '__main__':
    root = Root()
    root.mainloop()
