from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
import customtkinter
import numpy as np
import cv2
import io
from PIL import Image, ImageTk
from spade.model import Pix2PixModel
from spade.dataset import get_transform
from torchvision.transforms import ToPILImage
from merger import Merger
#from dynamic_style_transfer.gui.main_style_transfer_widget import MainStyleTransferWidget
import os
os.environ['PATH'] = os.environ['PATH'] + ';C:\\Program Files\\gs\\gs10.00.0\\bin'  # replace with the actual path to Ghostscript on your system


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class Style(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.des = None

        # configure window(width,height)
        self.title("Stylize")
        self.geometry(f"{880}x{650}")
        self.minsize(880, 650)
        self.image_size = (250,250)
        self.toplevel_window = None
        
        # configure grid layout (4x4)
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)

        #Frames
        self.content_frame = customtkinter.CTkFrame(self)
        self.content_frame.grid(row=0, column=0,sticky="nsew")
        self.content_frame.grid_columnconfigure((0,2),weight=1)
        self.content_frame.grid_columnconfigure(1,weight=2)
        

        self.style_frame = customtkinter.CTkFrame(self)
        self.style_frame.grid(row=0, column=1,sticky="nsew")
        self.style_frame.grid_columnconfigure((0,2),weight=1)
        self.style_frame.grid_columnconfigure(1,weight=2)
        

        self.output_frame = customtkinter.CTkFrame(self)
        self.output_frame.grid(row=1, column=0,columnspan=2,sticky="nsew")
        self.output_frame.grid_columnconfigure((0,2),weight=1)
        self.output_frame.grid_columnconfigure(1,weight=2)
       

        #Content image display
        #label for the generated image
        self.content_label = customtkinter.CTkLabel(self.content_frame,text="Content Image:", anchor="w")
        self.content_label.grid(row=0, column=1, padx=20, pady=(10, 0))
        img = customtkinter.CTkImage(Image.open('C:/Users/nirva/Desktop/UniStuff/Project/Code/generatedimage.png'),size=self.image_size)
        self.lmain = customtkinter.CTkLabel(self.content_frame,image=img ,text=None)
        self.lmain.grid(row=1, column=1,padx=10, pady= 10)


        #Stylize section
        self.style_label = customtkinter.CTkLabel(self.style_frame,text="Style Image:", anchor="w")
        self.style_label.grid(row=0, column=1, padx=20, pady=(10, 0))
        #buttons(need to remove then later once image is added)
        self.sidebar_button_2 = customtkinter.CTkButton(self.style_frame, command=self.upload, text="Import Style Image")
        self.sidebar_button_2.grid(row=1, column=1, padx=20, pady=10)
        self.sidebar_button_2.grid_rowconfigure(2, weight=0)
        #####FOR DEFAULT STYLES SELECTION WINDOW#####
        # self.sidebar_button_3 = customtkinter.CTkButton(self.style_frame, command=self.openstyles, text="Default Styles")
        # self.sidebar_button_3.grid(row=2, column=1, padx=20, pady=10)
        # self.sidebar_button_3.grid_rowconfigure(2, weight=0)


        #Output section
        #label for the generated image
        self.content_label = customtkinter.CTkLabel(self.output_frame,text="Output Image:")
        self.content_label.grid(row=0, column=1, padx=20, pady=(10, 0))
        #merge button
        self.sidebar_button_2 = customtkinter.CTkButton(self.output_frame, command=self.merge, text="MERGE")
        self.sidebar_button_2.grid(row=1, column=1, padx=20, pady=10)
        
    def upload(self):
        # Show file dialog to select an image file
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        self.des = file_path
        # Open the image file using PIL
        image = Image.open(file_path)
    
        # Create a Tkinter-compatible photo image and display it in a Label widget
        photo = customtkinter.CTkImage(image,size=self.image_size)
        self.style_photo = customtkinter.CTkLabel(self.style_frame,image=photo ,text=None)
        self.style_photo.grid(row=1, column=1,padx=10, pady= 10)

        self.sidebar_button_2 = customtkinter.CTkButton(self.style_frame, command=self.upload, text="Upload image")
        self.sidebar_button_2.grid(row=2, column=1, padx=20, pady=10)
        self.sidebar_button_2.grid_rowconfigure(2, weight=0) 

    def uploadselect(self,file_path):
        self.des = file_path
        # Open the image file using PIL
        image = Image.open(file_path)
    
        # Create a Tkinter-compatible photo image and display it in a Label widget
        photo = customtkinter.CTkImage(image,size=self.image_size)
        self.style_photo = customtkinter.CTkLabel(self.style_frame,image=photo ,text=None)
        self.style_photo.grid(row=1, column=1,padx=10, pady= 10)

        self.sidebar_button_2 = customtkinter.CTkButton(self.style_frame, command=self.upload, text="Upload image")
        self.sidebar_button_2.grid(row=2, column=1, padx=20, pady=10)
        self.sidebar_button_2.grid_rowconfigure(2, weight=0) 

    def merge(self):#<-----need to apply nst model
        m = Merger()
        
        content_image = cv2.resize(cv2.imread('C:/Users/nirva/Desktop/UniStuff/Project/Code/generatedimage.png'), (224, 224))
        style_image = cv2.resize(cv2.imread(self.des), (224, 224))
        m_image = m.process(content_image,style_image)

        #output image to be displayed
        img = customtkinter.CTkImage(m_image,size=self.image_size)
        self.lmain = customtkinter.CTkLabel(self.output_frame,image=img ,text=None)
        self.lmain.grid(row=1, column=1,padx=10, pady= 10)

        #merge button after merge is made
        self.sidebar_button_2 = customtkinter.CTkButton(self.output_frame, command=self.merge, text="MERGE")
        self.sidebar_button_2.grid(row=2, column=1, padx=20, pady=10)
        self.sidebar_button_2.grid_rowconfigure(2, weight=0)
        


    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def openstyles(self):
        #for the top level
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()

##### UI OF DEFAULT STYLES SELECTION WINDOW #####

class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Default Styles")
        self.geometry("450x500")
        self.minsize(450, 500)

        # create scrollable label and button frame
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.scrollable_label_button_frame = ScrollableLabelButtonFrame(master=self, width=1000, command=self.label_button_frame_event, corner_radius=0)
        self.scrollable_label_button_frame.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        imgname=['autumn_landscape.jpg','colors.jpg','feathers.jpg','girl.jpg','guitar.jpg','horse.jpg','mosaic.jpg','mosaic3.jpg','on_white_II.jpg','rain_princess.jpg','udnie.jpg']
        for i in range(0,len(imgname)):  # add items with images
            self.scrollable_label_button_frame.add_item(f"Image {i+1}", image=customtkinter.CTkImage(Image.open(os.path.join(current_dir, "style_images" ,imgname[i])),size=(200,200)))

    def label_button_frame_event(self, item):
        print(f"label button frame clicked: {item}")
    
class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.label_list = []
        self.button_list = []

    def add_item(self, item, image=None):
        label = customtkinter.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(self, text="Select", width=100, height=24)
        if self.command is not None:
            button.configure(command=lambda: self.command(item))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return
#run the app
if __name__ == "__main__":
    app = Style()
    app.mainloop() 