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

        self.rotation_var = tk.IntVar()
        self.rotation_var.set(0)  # 初始旋轉角度
        self.rotation_slider = Scale(root, label="旋轉角度", orient=tk.HORIZONTAL, from_=0, to=360,
                                     variable=self.rotation_var, command=self.rotate_image)
        self.rotation_slider.pack()

        self.button_extract = tk.Button(root, text="擷取", command=self.extract_region)
        self.button_extract.pack()

        self.button_save = tk.Button(root, text="存檔", command=self.save_image)
        self.button_save.pack()

        self.image_path = None
        self.image = None
        self.resized_image = None
        self.processed_image = None
        self.extracted_region = None
        self.selection_rectangle = None

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

    def rotate_image(self, event=None):
        if self.resized_image is not None:
            rotation_angle = self.rotation_var.get()
            rows, cols, _ = self.resized_image.shape
            rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), rotation_angle, 1)
            self.processed_image = cv2.warpAffine(self.resized_image, rotation_matrix, (cols, rows))
            self.display_image("processed")  # 顯示旋轉後的圖像

    def extract_region(self):
        if self.resized_image is not None:
            # 開始選取矩形區域
            self.canvas_original.bind("<ButtonPress-1>", self.on_press)
            self.canvas_original.bind("<B1-Motion>", self.on_drag)
            self.canvas_original.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        # 記錄起點位置
        self.start_x = self.canvas_original.canvasx(event.x)
        self.start_y = self.canvas_original.canvasy(event.y)

        # 刪除先前的矩形
        if self.selection_rectangle:
            self.canvas_original.delete(self.selection_rectangle)

        # 建立新的矩形
        self.selection_rectangle = self.canvas_original.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_drag(self, event):
        cur_x = self.canvas_original.canvasx(event.x)
        cur_y = self.canvas_original.canvasy(event.y)

        # 更新矩形的座標
        self.canvas_original.coords(self.selection_rectangle, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas_original.canvasx(event.x)
        end_y = self.canvas_original.canvasy(event.y)

        # 截取選區內的圖像
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        self.extracted_region = self.resized_image[int(y1):int(y2), int(x1):int(x2)]

        # 顯示截取的圖像
        self.display_extracted_image(self.extracted_region)

        # 解綁事件，避免重複觸發
        self.canvas_original.unbind("<ButtonPress-1>")
        self.canvas_original.unbind("<B1-Motion>")
        self.canvas_original.unbind("<ButtonRelease-1>")

    def display_extracted_image(self, region):
        if region is not None:
            region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
            region_pil = Image.fromarray(region_rgb)
            region_tk = ImageTk.PhotoImage(region_pil)

            height, width = region_rgb.shape[:2]

            self.canvas_processed.config(width=width, height=height)
            self.canvas_processed.create_image(0, 0, anchor=tk.NW, image=region_tk)
            self.canvas_processed.image = region_tk

    def save_image(self):
        if self.processed_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"),
                                                                                        ("JPEG files", "*.jpg;*.jpeg"),
                                                                                        ("All files", "*.*")])
            if file_path:
                if self.extracted_region is not None:
                    # 如果有選取區域，則保存選取區域的圖像
                    cv2.imwrite(file_path, self.extracted_region)
                else:
                    # 如果沒有選取區域，則保存處理後的整張圖像
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
