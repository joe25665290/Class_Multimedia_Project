import cv2
import tkinter as tk
from tkinter import filedialog, Scale
from PIL import Image, ImageTk
import numpy as np
import collections

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")

        self.canvas_original = tk.Canvas(root)
        self.canvas_original.pack(side=tk.LEFT)

        self.canvas_processed = tk.Canvas(root)
        self.canvas_processed.pack(side=tk.RIGHT)

        self.button_open = tk.Button(root, text="開檔", command=self.open_image)
        self.button_open.pack()

        self.button_flip = tk.Button(root, text="翻轉", command=lambda: self.add_image_effect("flip"))
        self.button_flip.pack()

        self.button_gray = tk.Button(root, text="灰階", command=lambda: self.add_image_effect("gray"))
        self.button_gray.pack()

        self.button_negative = tk.Button(root, text="負片", command=lambda: self.add_image_effect("negative"))
        self.button_negative.pack()

        self.button_binary = tk.Button(root, text="二值化", command=lambda: self.add_image_effect("binary"))
        self.button_binary.pack()

        self.threshold_var = tk.IntVar()
        self.threshold_var.set(127)
        self.threshold_slider = Scale(root, label="閾值", orient=tk.HORIZONTAL, from_=0, to=255,
                                      variable=self.threshold_var, command=self.produce_image)
        self.threshold_slider.pack()

        self.rotation_var = tk.IntVar()
        self.rotation_var.set(0)
        self.rotation_slider = Scale(root, label="旋轉角度", orient=tk.HORIZONTAL, from_=0, to=360,
                                     variable=self.rotation_var, command=self.produce_image)
        self.rotation_slider.pack()

        self.gamma_var = tk.DoubleVar()
        self.gamma_var.set(1.0)
        self.gamma_slider = Scale(root, label="Gamma", orient=tk.HORIZONTAL, from_=0.1, to=5.0,
                                  resolution=0.1, variable=self.gamma_var, command=self.produce_image)
        self.gamma_slider.pack()

        self.button_extract = tk.Button(root, text="區域放大", command=self.extract_region)
        self.button_extract.pack()

        self.button_erode = tk.Button(root, text="侵蝕", command=lambda: self.add_image_effect("erode"))
        self.button_erode.pack()

        self.button_dilate = tk.Button(root, text="膨脹", command=lambda: self.add_image_effect("dilate"))
        self.button_dilate.pack()

        self.kernel_size_var = tk.IntVar()
        self.kernel_size_var.set(3)  # 设置初始内核大小
        self.kernel_size_slider = Scale(root, label="內核大小", orient=tk.HORIZONTAL, from_=1, to=15,resolution=2,
                                        variable=self.kernel_size_var, command=self.produce_image)
        self.kernel_size_slider.pack()

        self.button_save = tk.Button(root, text="存檔", command=self.save_image)
        self.button_save.pack()

        self.show_width = 255
        self.image_path = None
        self.image = None
        self.resized_image = None
        self.processed_image = None
        self.resized_processed_image = None
        self.retrieve_image = None
        self.selection_rectangle = None
        self.image_effect = []

    def add_image_effect(self, effect):
        self.image_effect.append(effect)
        self.produce_image()

    def produce_image(self, _=None, image=None):
        if self.image is not None:
            if image is not None:
                self.retrieve_image = image
            self.processed_image = self.retrieve_image.copy()  # Make a copy to avoid modifying the original
            effect = collections.Counter(self.image_effect)
            if effect["flip"] % 2:
                self.flip_image()
            if effect["gray"] % 2:
                self.convert_to_gray()
            if effect["negative"] % 2:
                self.apply_negative()
            if effect["binary"] % 2:
                self.apply_binary()
            for i in self.image_effect:
                if i == "dilate":
                    self.dilate_image()
                elif i == "erode":
                    self.erode_image()
            
            self.rotate_image()
            self.adjust_gamma()
            
            self.display_image("processed")

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path
            self.image = cv2.imread(file_path)
        if self.image is None:
            print("不支援此圖片檔名或其他錯誤")
            return
        self.processed_image = self.image.copy()
        self.retrieve_image = self.image.copy()
        self.resized_image = self.resize_image(self.image)
        self.display_image("original")
        self.image_effect = []

    def resize_image(self, image):
        if image is not None:
            height = int(image.shape[0] * (self.show_width / image.shape[1]))
            return cv2.resize(image, (self.show_width, height))

    def flip_image(self):
        self.processed_image = cv2.flip(self.processed_image, 1)

    def convert_to_gray(self):
        self.processed_image = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)

    def apply_negative(self):
        self.processed_image = 255 - self.processed_image

    def apply_binary(self, event=None):
        threshold_value = self.threshold_var.get()
        _, self.processed_image = cv2.threshold(self.processed_image, threshold_value, 255, cv2.THRESH_BINARY)

    def rotate_image(self, event=None):
        rotation_angle = self.rotation_var.get()
        if len(self.processed_image.shape) == 2:
            rows, cols = self.processed_image.shape
        else:
            rows, cols, _ = self.processed_image.shape
        rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), rotation_angle, 1)
        self.processed_image = cv2.warpAffine(self.processed_image, rotation_matrix, (cols, rows))

    def adjust_gamma(self):
        gamma_value = self.gamma_var.get()
        gamma_corrected = np.power(self.processed_image / 255.0, gamma_value)
        self.processed_image = np.uint8(255 * gamma_corrected)
    
    def erode_image(self):
        kernel_size = self.kernel_size_var.get()
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        self.processed_image = cv2.erode(self.processed_image, kernel)
        self.display_image("processed")

    def dilate_image(self):
        kernel_size = self.kernel_size_var.get()
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        self.processed_image = cv2.dilate(self.processed_image, kernel)
        self.display_image("processed")

    def extract_region(self):
        if self.resized_image is not None:
            self.canvas_original.bind("<ButtonPress-1>", self.on_press)
            self.canvas_original.bind("<B1-Motion>", self.on_drag)
            self.canvas_original.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = self.canvas_original.canvasx(event.x)
        self.start_y = self.canvas_original.canvasy(event.y)

        if self.selection_rectangle:
            self.canvas_original.delete(self.selection_rectangle)

        self.selection_rectangle = self.canvas_original.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_drag(self, event):
        cur_x = self.canvas_original.canvasx(event.x)
        cur_y = self.canvas_original.canvasy(event.y)
        self.canvas_original.coords(self.selection_rectangle, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas_original.canvasx(event.x)
        end_y = self.canvas_original.canvasy(event.y)

        t = self.image.shape[1] / self.show_width

        x1 = min(self.start_x, end_x) * t
        y1 = min(self.start_y, end_y) * t
        x2 = max(self.start_x, end_x) * t
        y2 = max(self.start_y, end_y) * t

        self.produce_image(image=self.image[int(y1):int(y2), int(x1):int(x2)])

        self.canvas_original.unbind("<ButtonPress-1>")
        self.canvas_original.unbind("<B1-Motion>")
        self.canvas_original.unbind("<ButtonRelease-1>")

    def save_image(self):
        if self.processed_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"),
                                                                                        ("JPEG files", "*.jpg;*.jpeg"),
                                                                                        ("All files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, self.processed_image)

    def display_image(self, mode):
        if mode == "original" and self.resized_image is not None:
            image_rgb = cv2.cvtColor(self.resized_image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            image_tk = ImageTk.PhotoImage(image_pil)

            height, width = image_rgb.shape[:2]
            canvas = self.canvas_original

        elif mode == "processed" and self.processed_image is not None:
            self.resized_processed_image = self.resize_image(self.processed_image)
            if len(self.resized_processed_image.shape) == 2:
                image_rgb = cv2.cvtColor(self.resized_processed_image, cv2.COLOR_GRAY2RGB)
            else:
                image_rgb = cv2.cvtColor(self.resized_processed_image, cv2.COLOR_BGR2RGB)

            image_pil = Image.fromarray(image_rgb)
            image_tk = ImageTk.PhotoImage(image_pil)

            height, width = image_rgb.shape[:2]
            canvas = self.canvas_processed

        canvas.config(width=width, height=height)
        canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        canvas.image = image_tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
