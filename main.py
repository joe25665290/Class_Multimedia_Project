import cv2
import tkinter as tk
from tkinter import filedialog, Scale
from PIL import Image, ImageTk
import numpy as np

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

        self.button_flip = tk.Button(root, text="翻轉", command=self.flip_image)
        self.button_flip.pack()

        self.button_gray = tk.Button(root, text="灰階", command=self.convert_to_gray)
        self.button_gray.pack()

        self.button_negative = tk.Button(root, text="負片", command=self.apply_negative)
        self.button_negative.pack()

        self.button_binary = tk.Button(root, text="二值化", command=self.apply_binary)
        self.button_binary.pack()

        self.threshold_var = tk.IntVar()
        self.threshold_var.set(127)  # 初始閾值
        self.threshold_slider = Scale(root, label="閾值", orient=tk.HORIZONTAL, from_=0, to=255,
                                      variable=self.threshold_var, command=self.apply_binary)
        self.threshold_slider.pack()

        self.button_save = tk.Button(root, text="存檔", command=self.save_image)
        self.button_save.pack()

        self.image_path = None
        self.image = None
        self.resized_image = None
        self.processed_image = None

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image_path = file_path
            self.image = cv2.imread(file_path)
            self.resize_image()
            self.display_image("original")  # 顯示原圖

    def resize_image(self):
        if self.image is not None:
            # 計算等比例縮放後的高度
            width = 255
            height = int(self.image.shape[0] * (width / self.image.shape[1]))
            self.resized_image = cv2.resize(self.image, (width, height))

    def flip_image(self):
        if self.resized_image is not None:
            self.processed_image = cv2.flip(self.resized_image, 1)  # 1表示水平翻轉
            self.display_image("processed")  # 顯示翻轉後的圖像

    def convert_to_gray(self):
        if self.resized_image is not None:
            self.processed_image = cv2.cvtColor(self.resized_image, cv2.COLOR_BGR2GRAY)
            self.display_image("processed")  # 顯示灰階圖像

    def apply_negative(self):
        if self.resized_image is not None:
            self.processed_image = 255 - self.resized_image
            self.display_image("processed")  # 顯示負片

    def apply_binary(self, event=None):
        if self.resized_image is not None:
            threshold_value = self.threshold_var.get()
            _, self.processed_image = cv2.threshold(self.resized_image, threshold_value, 255, cv2.THRESH_BINARY)
            self.display_image("processed")  # 顯示二值化後的圖像

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
            if len(self.processed_image.shape) == 2:  # 灰階圖像
                processed_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_GRAY2RGB)
            else:
                processed_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)

            processed_pil = Image.fromarray(processed_rgb)
            processed_tk = ImageTk.PhotoImage(processed_pil)

            height, width = processed_rgb.shape[:2]
            canvas = self.canvas_processed

        canvas.config(width=width, height=height)
        canvas.create_image(0, 0, anchor=tk.NW, image=image_tk if mode == "original" else processed_tk)
        canvas.image = image_tk if mode == "original" else processed_tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
