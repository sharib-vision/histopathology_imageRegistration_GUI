#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 13:41:16 2019

@author: sharib
"""

import tkinter as tk
from tkinter import filedialog

from tkinter import RIGHT, BOTH, RAISED
from tkinter.ttk import Frame, Button, Style

# for plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from rigid_reg import HistopathologyRegistration

import skimage
from skimage import io
import numpy as np


# for choice of registration (making this global)


class MainVisual(tk.Frame):
    # choose the files and visualise the tracks on the data
    def sel(self):
        selection = "You selected the option " + str(tk.IntVar().get())
        self.b.config(text = selection)

    def __init__(self, master):

        self.v = tk.IntVar()

        tk.Frame.__init__(self, master)
        self.master = master
        self.initUI_registration()
        self.init_window()
        self.initUI()

        self.sourceImage_file=" "
        self.targetImage_file=" "
        self.registeredImage=" "
        self.track_file=" "
        self.movie=[]
        self.parameters=" "

        self.button1 = tk.Button(text="SourceImage", command=self.select_source, width=10, font=('Helvetica', 18, 'bold'), relief=tk.GROOVE)
        self.button1.place(x = 20, y = 30 + 1*70, width=150, height=50)
#        self.button1.grid(row=4, column=1)
        self.button2 = tk.Button(text="TargetImage", command=self.select_target, width=10, font=('Helvetica', 18, 'bold'), relief=tk.GROOVE)
        self.button2.place(x = 20, y = 30 + 2*70, width=150, height=50)
#        self.button2.grid(row=6, column=1)
        self.button3 = tk.Button(text="ShowImage", command=self.visualize_SourceTarget, width=10, font=('Helvetica', 18, 'bold'), relief=tk.GROOVE)
        self.button3.place(x = 20, y = 30 + 3*70, width=150, height=50)

        self.button4 = tk.Button(text="OverlayImage", command=self.visualize_colorOverlay, width=10, font=('Helvetica', 18, 'bold'), relief=tk.GROOVE)
        self.button4.place(x = 20, y = 30 + 4*70, width=150, height=50)

        self.button5 = tk.Button(text="Registered", command=self.show_registered, width=10, font=('Helvetica', 18, 'bold'), relief=tk.GROOVE)
        self.button5.place(x = 20, y = 30 + 5*70, width=150, height=50)

        self.button6 = tk.Button(text="Overlay_reg", command=self.visualize_colorOverlay_registered, width=10, font=('Helvetica', 18, 'bold'), relief=tk.GROOVE)
        self.button6.place(x = 20, y = 30 + 6*70, width=150, height=50)


    def initUI(self):
#        self.master.title("Buttons")
        self.style = Style()
        self.style.theme_use("default")
        frame = Frame(self, relief=RAISED, borderwidth=1)
        frame.pack(fill=BOTH, expand=True)
        self.pack(fill=BOTH, expand=True)
        closeButton = Button(self, text="Close",  command=self.client_exit)
        closeButton.pack(side=RIGHT, padx=5, pady=5)
        okButton = Button(self, text="OK", command=self.perform_registration)
        okButton.pack(side=RIGHT)

    def initUI_registration(self):
        self.var = tk.IntVar()
        self.var = tk.StringVar()
        self.var.set("1") # initialize

        #frame = Frame(self.master, relief=RAISED, borderwidth=1)
        MODES = [ ("Rigid", "1"), ("Non-rigid", "2"),]
        for text, mode in MODES:
            #            command=self.sel
            self.b = tk.Radiobutton(text=text, variable=self.var, value=mode, font=('Helvetica', 18, 'bold'), )
            self.b.pack(side=tk.TOP, anchor=tk.W)

#Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("TK-InterGUI")
        # allowing the widget to take the full space of the root window
#        self.pack(fill=BOTH, expand=1)
        # creating a menu instance
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)
        # create the file object)
        file = tk.Menu(menu)
        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        file.add_command(label="Exit", command=self.client_exit)
        #added "file" to our menu
        menu.add_cascade(label="File", menu=file)
        # create the file object)
        edit = tk.Menu(menu)
        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        edit.add_command(label="Undo")
        #added "file" to our menu
        menu.add_cascade(label="Edit", menu=edit)

    def client_exit(self):
        exit()

    def select_source(self):
        # Allow user to select movie
#        filename = tk.filedialog.askopenfilename(filetypes = [("All files", "*.*")])
        filename = tk.filedialog.askopenfilename()
        self.sourceImage_file=filename

    def select_target(self):
        # Allow user to select movie
        #        filename = tk.filedialog.askopenfilename(filetypes = [("All files", "*.*")])
        filename = tk.filedialog.askopenfilename()
        self.targetImage_file=filename

    # reduantant
    def select_track(self):
        # Allow user to select a file with tracking data
        global folder_path_output
        filename = tk.filedialog.askopenfilename()
        self.track_file=filename

    def visualize_colorOverlay(self):
        #todo to make overlay images
        import cv2
        sourceImage=cv2.imread(self.sourceImage_file, 1)
        targetImage=cv2.imread(self.targetImage_file, 1)
#        height, width, _ = targetImage.shape

        try:
            height, width, _ = targetImage.shape
            # print("checked for shape", targetImage.shape)
        except AttributeError:
            print("shape not found")

        sourceImage_resized = cv2.resize(sourceImage, (width,height))
        outImage = cv2.subtract(sourceImage_resized, targetImage)
        fig = plt.figure(figsize=(5,5))
        plt.axis('off')
        plt.imshow(outImage)
        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(x = 180, y = 100, width=600, height=420)

    def show_registered(self):
        #todo to make overlay images
        import cv2
        sourceImage=cv2.imread(self.sourceImage_file, 1)
        targetImage=cv2.imread(self.targetImage_file, 1)
        rows, cols, _ = targetImage.shape

        M = np.float32([ [1, 0, np.fabs(self.parameters[0])], [0, 1, np.fabs(self.parameters[1])] ])
        self.registeredImage = cv2.warpAffine(sourceImage, M , (cols, rows))

        # outImage = cv2.subtract(self.registeredImage, targetImage)

        fig = plt.figure(figsize=(5,5))
        plt.axis('off')
        plt.imshow(self.registeredImage)
        # plt.imshow(outImage)
        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(x = 180, y = 100, width=600, height=420)

    def visualize_colorOverlay_registered(self):
        #todo to make overlay images
        import cv2

        targetImage=cv2.imread(self.targetImage_file, 1)

        try:
            outImage = cv2.subtract(self.registeredImage, targetImage)
        except AttributeError:
            print("first press registered and then continue")

        fig = plt.figure(figsize=(5,5))
        plt.axis('off')
        plt.imshow(outImage)
        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(x = 180, y = 100, width=600, height=420)


    def visualize_SourceTarget(self):
        #todo to make overlay images
        self.source=skimage.io.imread(self.sourceImage_file)
        self.target=skimage.io.imread(self.targetImage_file)

        fig = plt.figure(figsize=(5,5))
        plt.axis('off')
        plt.imshow(self.source)
        self.canvas = FigureCanvasTkAgg(fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(x = 180, y = 100, width=600, height=420)

        # self.canvas.get_tk_widget().grid(row=6, column=2, columnspan=4)
        fig1 = plt.figure(figsize=(5,5))
        plt.axis('off')
        plt.imshow(self.target)
        # DrawingArea
        self.canvas = FigureCanvasTkAgg(fig1, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().place(x = 780, y = 100, width=600, height=420)

    def perform_registration(self):
        useMI = 1
        # selecting rigd/non-rigid according to the choice
        print ("Selection:",self.var.get())

        if self.var.get() == "1":
            print('rigid-registration...')
            transformationFILE = self.sourceImage_file.split('.')[0]+'.txt'
            if useMI:
                tx_parameters = HistopathologyRegistration.rigid_registration_MI(self.sourceImage_file, self.targetImage_file, transformationFILE)
            else:
                tx_parameters = HistopathologyRegistration.rigid_registration(self.sourceImage_file, self.targetImage_file, transformationFILE)

            self.parameters = tx_parameters.GetParameters()
        elif self.var.get() == "2":
            print('NON-rigid registration...')
            useMI = 0
            transformationFILE = self.sourceImage_file.split('.')[0]+'.txt'
            if useMI:
                tx_parameters = HistopathologyRegistration.rigid_registration_MI(self.sourceImage_file, self.targetImage_file, transformationFILE)
            else:
                tx_parameters = HistopathologyRegistration.non_rigid(self.sourceImage_file, self.targetImage_file, transformationFILE)

            self.parameters = tx_parameters.GetParameters()
        else:
            print('select either rigid or non-rigid registration')

        
class MainApplication(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        parent.title("TrackHandler")
        parent.configure(background='white')
        parent.geometry("1400x600") #Width x Height
        self.main = MainVisual(parent)
#        self.main.pack(side="left")

if __name__ == "__main__":
    root = tk.Tk()
    tk.Label(root, text="Image viewer for Histopathology Image Registration",
             fg = "light green",
             bg = "dark green",
             font = "Helvetica 16 bold italic").pack()
#    tk.Label(root, text="Please run scripts for performing batch processing of files",
#             fg = "light green",
#             bg = "dark green",
#             font = "Helvetica 16 bold italic").pack()
    MainApplication(root)
    root.mainloop()
