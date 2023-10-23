from tkinter import *
from styleui import Style
import tkinter.messagebox
import customtkinter
import numpy as np
import cv2
import io
from PIL import Image, ImageTk, ImageGrab
from spade.model import Pix2PixModel
from spade.dataset import get_transform
from torchvision.transforms import ToPILImage
#from dynamic_style_transfer.gui.main_style_transfer_widget import MainStyleTransferWidget
import os
os.environ['PATH'] = os.environ['PATH'] + ';C:\\Program Files\\gs\\gs10.00.0\\bin'  # replace with the actual path to Ghostscript on your system


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("AI Art Canvas")
        self.geometry(f"{1180}x{512}")
        self.minsize(1180, 512)
        
        # configure grid layout (4x4)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1), weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="ns")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.clear_canvas, text='Clear')
        self.sidebar_button_1.grid(row=0, column=0, padx=20, pady=10)

        #generate button
        self.sidebar_button_2 = customtkinter.CTkButton(self, command=self.generate, text="Generate")
        self.sidebar_button_2.grid(row=2, column=1, padx=20, pady=10)
        self.sidebar_button_2.grid_rowconfigure(2, weight=0)

        #style button
        self.sidebar_button_2 = customtkinter.CTkButton(self, command=self.openwin, text="Style", state="disabled")#<-----DONT FORGET TO DISABLE LATER
        self.sidebar_button_2.grid(row=2, column=2, padx=20, pady=10)
        self.sidebar_button_2.grid_rowconfigure(2, weight=0)
        
        #brush stroke slider
        self.slider_1 = customtkinter.CTkSlider(self.sidebar_frame, from_=0, to=100, command=self.show_value)
        self.slider_1.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        #brush stroke label
        self.stroke_label = customtkinter.CTkLabel(self.sidebar_frame,text="Stroke size: 50", anchor="w")
        self.stroke_label.grid(row=1, column=0, padx=20, pady=(10, 0))

        #color palatte frame
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text='Color Palatte: ', anchor="w")
        self.appearance_mode_label.grid(row=3, column=0, padx=20, pady=(10, 0))

        self.colorbar_frame = customtkinter.CTkFrame(self.sidebar_frame, width=140, corner_radius=0)
        self.colorbar_frame.grid(row=4, column=0, sticky="new")

        self.colorbar_canvas = Canvas(self.colorbar_frame, width=265, highlightthickness=0)
        self.colorbar_canvas.grid(row=0, column=0, sticky="nsew")

        self.button_scrollbar = customtkinter.CTkScrollbar(self.colorbar_frame, orientation="vertical", command=self.colorbar_canvas.yview)
        self.button_scrollbar.grid(row=0, column=1, sticky="ns")

        # connect textbox scroll event to CTk scrollbar
        self.colorbar_canvas.configure(yscrollcommand=self.button_scrollbar.set)
        self.colorbar_canvas.bind('<Configure>',lambda e: self.colorbar_canvas.configure(scrollregion= second_frame.bbox(all)))

        second_frame= customtkinter.CTkFrame(self.colorbar_canvas, fg_color="#252525", corner_radius=0)
        self.colorbar_canvas.create_window((0,0), window=second_frame, anchor="nw")

        colorMap = [
            { 'color': "#9a83ff", "id": 154, "label": "sea" },
            { 'color': "#69ffff", "id": 105, "label": "cloud", "labelColor": "black" },
            { 'color': "#6e2505", "id": 110, "label": "dirt" },
            { 'color': "#60b000", "id": 96, "label": "bush" },
            { 'color': "#7bff00", "id": 123, "label": "grass", "labelColor": "black" },
            { 'color': "#861000", "id": 134, "label": "mountain" },
            { 'color': "#947f98", "id": 148, "label": "road" },
            { 'color': "#9cc4df", "id": 156, "label": "sky" },
            { 'color': "#a8ff00", "id": 168, "label": "tree", "labelColor": "black" },
            { 'color': "#760072", "id": 118, "label": "flower" },
            { 'color': "#77a8ef", "id": 119, "label": "fog", "labelColor": "black" },
            { 'color': "#7e8f00", "id": 126, "label": "hill" },
            { 'color': "#80494a", "id": 128, "label": "leaves" },
            { 'color': "#93d1ff", "id": 147, "label": "river", "labelColor": "black" },
            { 'color': "#9effff", "id": 158, "label": "snow", "labelColor": "black" },
        ]
        self.pen_color = '#384f83'
        i=0
        #to create color buttons
        for color in colorMap:
            customtkinter.CTkButton(second_frame,fg_color=color['color'],hover_color=color['color'],text_color=color.setdefault("labelColor","white"),command=lambda col = color['color']:self.select_color(col),text=color["label"]).grid(row=i, column=0, padx=45,pady=5)
            i+=1

        #canvas
        self.window = 512
        self.canvas = Canvas(self, width=self.window, height=self.window, highlightthickness=0)#bg=colorMap[7]['color']
        self.canvas.grid(row=0, column=1,padx=10, pady= 10)
        self.canvas.bind("<B1-Motion>", self.draw_brushstroke)

        #label for the generated image
        self.lmain = customtkinter.CTkLabel(self,text=None)
        self.lmain.grid(row=0, column=2,padx=10, pady= 10)
        
        #self.photo = Canvas(self, width=self.window, height=self.window, bg="#252525")
        #self.photo.grid(row=0, column=2,padx=10, pady= 10)
    
    def show_value(self,value):
        value = self.slider_1.get()
        self.stroke_label.configure(text="Stroke size: {:.2f}".format(value))

    def draw_brushstroke(self,event):
        x, y = event.x, event.y
        self.canvas.create_oval(x, y, x+1, y+1, width=self.slider_1.get(), fill=self.pen_color, outline=self.pen_color)   
    
    def select_color(self,col):
        self.pen_color = col
        
    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def clear_canvas(self):
        self.window = 512
        self.canvas = Canvas(self, width=self.window, height=self.window, highlightthickness=0)#bg=colorMap[7]['color']
        self.canvas.grid(row=0, column=1,padx=10, pady= 10)
        self.canvas.bind("<B1-Motion>", self.draw_brushstroke)

    def openwin(self):     
##### SECOND WINDOW ###################
        app.destroy()
        styleui = Style()
        styleui.mainloop() #running 2nd window
###########################################

    #function for generate button
    def generate(self):
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Grab the screen content within the specified region
        image = ImageGrab.grab(bbox=(x, y, x + width, y + height))

        # Save the image to the specified file path
        image.save('C:/Users/nirva/Desktop/UniStuff/Project/Code/canvasimage.png')
        labelmap = Image.open('C:/Users/nirva/Desktop/UniStuff/Project/Code/canvasimage.png')#use it as label map

        labelmap_np = np.asarray(labelmap)
        # Read image data using OpenCV
        labelmap_cv = cv2.cvtColor(labelmap_np, cv2.COLOR_RGB2BGR)
        labelmap_cv = labelmap_cv[:,:,2]
        #the functions used for evaluating the sketch and output the real image
        image = self.evaluate(labelmap_cv)
        rimage = self.to_image(image)
        rimage.save('C:/Users/nirva/Desktop/UniStuff/Project/Code/generatedimage.png')

        #display the image on the lmain label
        img = customtkinter.CTkImage(rimage,size=(450,450))
        self.lmain.configure(image=img)
        #enable Stylize button
        self.sidebar_button_2 = customtkinter.CTkButton(self, command=self.openwin, text="Style")
        self.sidebar_button_2.grid(row=2, column=2, padx=20, pady=10)
        self.sidebar_button_2.grid_rowconfigure(2, weight=0)

    #to evaluate the sketch
    def evaluate(self,labelmap):
        opt = {
            'label_nc': 182, # num classes in coco model
            'crop_size': 512,
            'load_size': 512,
            'aspect_ratio': 1.0,
            'isTrain': False,
            'checkpoints_dir': './pretrained',
            'which_epoch': 'latest',
            'use_gpu': False
        }
        model = Pix2PixModel(opt)
        model.eval()

        image = Image.fromarray(np.array(labelmap).astype(np.uint8))#pil image

        transform_label = get_transform(opt, method=Image.NEAREST, normalize=False)
        # transforms.ToTensor in transform_label rescales image from [0,255] to [0.0,1.0]
        # lets rescale it back to [0,255] to match our label ids
        label_tensor = transform_label(image) * 255
        label_tensor[label_tensor == 255] = opt['label_nc'] # 'unknown' is opt.label_nc
        print("label_tensor:", label_tensor.shape)

        # not using encoder, so creating a blank image...
        transform_image = get_transform(opt)
        image_tensor = transform_image(Image.new('RGB', (500, 500)))

        data = {
            'label': label_tensor.unsqueeze(0),
            'instance': label_tensor.unsqueeze(0),
            'image': image_tensor.unsqueeze(0)
        }
        print(data['label'])
        generated = model(data, mode='inference')
        print("generated_image:", generated.shape)

        return generated
    #to convert the generated image to PIL image
    def to_image(self, generated):
        to_img = ToPILImage()
        normalized_img = ((generated.reshape([3, 512, 512]) + 1) / 2.0) * 255.0
        return to_img(normalized_img.byte().cpu())

#run the app
if __name__ == "__main__":
    app = App()
    app.mainloop()       
        
        
        #self.sidebar_button_3.configure(state="disabled", text="Disabled CTkButton") #disable button 3
        # self.checkbox_2.configure(state="disabled")
        # self.switch_2.configure(state="disabled")
        # self.checkbox_1.select()
        # self.switch_1.select()
        # self.radio_button_3.configure(state="disabled")
        # self.appearance_mode_optionemenu.set("Dark")
        # self.scaling_optionemenu.set("100%")
        # self.optionmenu_1.set("CTkOptionmenu")
        # self.combobox_1.set("CTkComboBox")
        # self.slider_1.configure(command=self.progressbar_2.set)
        #self.slider_2.configure(command=self.progressbar_3.set)
        # self.progressbar_1.configure(mode="indeterminnate")
        # self.progressbar_1.start()
        # self.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
        #self.seg_button_1.configure(values=["CTkSegmentedButton", "Value 2", "Value 3"])
        #self.seg_button_1.set("Value 2")