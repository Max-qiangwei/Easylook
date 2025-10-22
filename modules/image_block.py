"""
单个图片块UI组件
包含原图显示、统计图显示和控制选项
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from PIL import Image, ImageTk
import os
from datetime import datetime

from modules.image_processor import ImageProcessor
from modules.language_manager import language_manager
from modules.color_picker import pick_color


class ImageBlock(ttk.Frame):
    """单个图片块组件"""
    
    def __init__(self, parent, block_id, **kwargs):
        """
        初始化图片块
        
        Args:
            parent: 父容器
            block_id: 块的ID（1-4）
        """
        super().__init__(parent, **kwargs)
        self.block_id = block_id
        self.image_data = None
        self.current_image_path = None
        
        # 默认散点图颜色（蓝色）
        self.plot_color = '#0000FF'
        
        # 默认点大小
        self.point_size = 1.0
        
        # 坐标轴范围
        self.x_min = 0
        self.x_max = 5
        self.y_min = 0
        self.y_max = 5
        
        # 注册语言变化观察者
        language_manager.register_observer(self.update_language)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI布局"""
        # 设置网格权重
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 创建控制面板
        self.create_control_panel()
        
        # 创建显示区域
        self.create_display_area()
        
        # 创建坐标轴控制面板
        self.create_axis_control_panel()
        
    def create_control_panel(self):
        """创建顶部控制面板"""
        self.control_frame = ttk.LabelFrame(self, text=f"{language_manager.get('image_block')} {self.block_id} {language_manager.get('control_panel')}")
        self.control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 颜色选择按钮（使用色块显示当前颜色）
        self.color_btn = tk.Button(
            self.control_frame,
            text="■",
            fg=self.plot_color,
            font=("Arial", 16),
            bd=0,  # 去除边框
            relief="flat",  # 平坦样式
            command=self.choose_color,
            width=2,
            highlightthickness=0  # 去除高亮边框
        )
        self.color_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # 颜色空间选择
        self.color_space_label = ttk.Label(self.control_frame, text=language_manager.get('color_space'))
        self.color_space_label.grid(row=0, column=1, padx=5, pady=5)
        self.color_space_var = tk.StringVar(value="rg_bg")
        self.color_space_combo = ttk.Combobox(
            self.control_frame, 
            textvariable=self.color_space_var,
            values=["rg_bg", "chromaticity"],
            state="readonly",
            width=15
        )
        self.color_space_combo.grid(row=0, column=2, padx=5, pady=5)
        
        # 绑定颜色空间变化事件
        self.color_space_combo.bind('<<ComboboxSelected>>', self.on_color_space_change)
        
        # 自定义降采样率输入
        self.sample_rate_label = ttk.Label(self.control_frame, text=language_manager.get('custom_sample_rate'))
        self.sample_rate_label.grid(row=0, column=3, padx=5, pady=5)
        self.sample_rate_var = tk.StringVar(value="10")
        self.sample_rate_entry = ttk.Entry(self.control_frame, textvariable=self.sample_rate_var, width=8)
        self.sample_rate_entry.grid(row=0, column=4, padx=5, pady=5)
        
        # 点大小控制
        self.point_size_label = ttk.Label(self.control_frame, text=language_manager.get('point_size'))
        self.point_size_label.grid(row=0, column=5, padx=5, pady=5)
        self.point_size_var = tk.StringVar(value="1.0")
        self.point_size_entry = ttk.Entry(self.control_frame, textvariable=self.point_size_var, width=8)
        self.point_size_entry.grid(row=0, column=6, padx=5, pady=5)
        
        # 上传按钮
        self.upload_btn = ttk.Button(
            self.control_frame,
            text=language_manager.get('upload_image'),
            command=self.upload_image
        )
        self.upload_btn.grid(row=0, column=7, padx=5, pady=5)
        
        # 刷新按钮
        self.refresh_btn = ttk.Button(
            self.control_frame,
            text=language_manager.get('refresh_plot'),
            command=self.refresh_plot,
            state="disabled"
        )
        self.refresh_btn.grid(row=0, column=8, padx=5, pady=5)
        
    def create_display_area(self):
        """创建图片和统计图显示区域"""
        display_frame = ttk.Frame(self)
        display_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # 配置网格权重
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)
        display_frame.grid_columnconfigure(1, weight=1)
        
        # 原图显示区域
        self.original_frame = ttk.LabelFrame(display_frame, text=language_manager.get('original_image'))
        self.original_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 创建原图显示容器
        image_container = ttk.Frame(self.original_frame)
        image_container.pack(expand=True, fill="both")
        
        # 创建原图显示标签
        self.original_label = ttk.Label(image_container, text=language_manager.get('please_upload'))
        self.original_label.pack(expand=True)
        
        # 创建图片信息面板
        self.info_frame = ttk.LabelFrame(self.original_frame, text=language_manager.get('image_info'))
        self.info_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        # 文件名标签
        self.filename_label = ttk.Label(self.info_frame, text=language_manager.get('filename') + " -")
        self.filename_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        # 文件大小标签
        self.filesize_label = ttk.Label(self.info_frame, text=language_manager.get('file_size') + " -")
        self.filesize_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        # 尺寸标签
        self.dimensions_label = ttk.Label(self.info_frame, text=language_manager.get('dimensions') + " -")
        self.dimensions_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        # 统计图显示区域
        self.plot_frame = ttk.LabelFrame(display_frame, text=language_manager.get('color_distribution'))
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(5, 4), dpi=100)
        # 调整子图参数以减少边距并确保x轴标签可见
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.12, right=0.95, top=0.95, bottom=0.15)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.grid(True, alpha=0.3)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")
        
    def create_axis_control_panel(self):
        """创建坐标轴控制面板"""
        self.axis_frame = ttk.LabelFrame(self, text=language_manager.get('axis_control'))
        self.axis_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        # X轴范围控制
        self.x_axis_label = ttk.Label(self.axis_frame, text=language_manager.get('x_axis_range'))
        self.x_axis_label.grid(row=0, column=0, padx=5, pady=5)
        self.x_min_label = ttk.Label(self.axis_frame, text=language_manager.get('min_value'))
        self.x_min_label.grid(row=0, column=1, padx=5, pady=5)
        self.x_min_var = tk.StringVar(value="0")
        x_min_entry = ttk.Entry(self.axis_frame, textvariable=self.x_min_var, width=5)
        x_min_entry.grid(row=0, column=2, padx=5, pady=5)
        
        self.x_max_label = ttk.Label(self.axis_frame, text=language_manager.get('max_value'))
        self.x_max_label.grid(row=0, column=3, padx=5, pady=5)
        self.x_max_var = tk.StringVar(value="5")
        x_max_entry = ttk.Entry(self.axis_frame, textvariable=self.x_max_var, width=5)
        x_max_entry.grid(row=0, column=4, padx=5, pady=5)
        
        # Y轴范围控制
        self.y_axis_label = ttk.Label(self.axis_frame, text=language_manager.get('y_axis_range'))
        self.y_axis_label.grid(row=0, column=5, padx=5, pady=5)
        self.y_min_label = ttk.Label(self.axis_frame, text=language_manager.get('min_value'))
        self.y_min_label.grid(row=0, column=6, padx=5, pady=5)
        self.y_min_var = tk.StringVar(value="0")
        y_min_entry = ttk.Entry(self.axis_frame, textvariable=self.y_min_var, width=5)
        y_min_entry.grid(row=0, column=7, padx=5, pady=5)
        
        self.y_max_label = ttk.Label(self.axis_frame, text=language_manager.get('max_value'))
        self.y_max_label.grid(row=0, column=8, padx=5, pady=5)
        self.y_max_var = tk.StringVar(value="5")
        y_max_entry = ttk.Entry(self.axis_frame, textvariable=self.y_max_var, width=5)
        y_max_entry.grid(row=0, column=9, padx=5, pady=5)
        
        # 应用按钮
        self.apply_btn = ttk.Button(
            self.axis_frame,
            text=language_manager.get('apply_range'),
            command=self.apply_axis_range
        )
        self.apply_btn.grid(row=0, column=10, padx=5, pady=5)
        
        # 重置按钮
        self.reset_btn = ttk.Button(
            self.axis_frame,
            text=language_manager.get('auto_range'),
            command=self.auto_axis_range
        )
        self.reset_btn.grid(row=0, column=11, padx=5, pady=5)
        
        # 保存图表按钮
        self.save_plot_btn = ttk.Button(
            self.axis_frame,
            text=language_manager.get('save_plot'),
            command=self.save_plot,
            state="disabled"
        )
        self.save_plot_btn.grid(row=0, column=12, padx=5, pady=5)
        
    def update_language(self):
        """更新界面语言"""
        # 更新控制面板
        self.control_frame.config(text=f"{language_manager.get('image_block')} {self.block_id} {language_manager.get('control_panel')}")
        self.color_space_label.config(text=language_manager.get('color_space'))
        self.sample_rate_label.config(text=language_manager.get('custom_sample_rate'))
        self.point_size_label.config(text=language_manager.get('point_size'))
        self.upload_btn.config(text=language_manager.get('upload_image'))
        self.refresh_btn.config(text=language_manager.get('refresh_plot'))
        
        # 更新显示区域
        self.original_frame.config(text=language_manager.get('original_image'))
        self.plot_frame.config(text=language_manager.get('color_distribution'))
        self.info_frame.config(text=language_manager.get('image_info'))
        
        # 更新图片信息标签
        if self.image_data and 'file_info' in self.image_data:
            file_info = self.image_data['file_info']
            self.filename_label.config(text=f"{language_manager.get('filename')} {file_info['filename']}")
            self.filesize_label.config(text=f"{language_manager.get('file_size')} {file_info['file_size']}")
            self.dimensions_label.config(text=f"{language_manager.get('dimensions')} {file_info['width']} x {file_info['height']} {language_manager.get('pixels')}")
        else:
            self.filename_label.config(text=language_manager.get('filename') + " -")
            self.filesize_label.config(text=language_manager.get('file_size') + " -")
            self.dimensions_label.config(text=language_manager.get('dimensions') + " -")
        
        # 更新原图标签（如果没有图片）
        if not self.current_image_path:
            self.original_label.config(text=language_manager.get('please_upload'))
        
        # 更新坐标轴控制面板
        self.axis_frame.config(text=language_manager.get('axis_control'))
        self.x_axis_label.config(text=language_manager.get('x_axis_range'))
        self.y_axis_label.config(text=language_manager.get('y_axis_range'))
        self.x_min_label.config(text=language_manager.get('min_value'))
        self.x_max_label.config(text=language_manager.get('max_value'))
        self.y_min_label.config(text=language_manager.get('min_value'))
        self.y_max_label.config(text=language_manager.get('max_value'))
        self.apply_btn.config(text=language_manager.get('apply_range'))
        self.reset_btn.config(text=language_manager.get('auto_range'))
        self.save_plot_btn.config(text=language_manager.get('save_plot'))
        
        # 刷新图表标题
        if self.image_data:
            self.display_plot()
            
    def on_color_space_change(self, event=None):
        """颜色空间选择变化事件"""
        if self.color_space_var.get() == "rg_bg":
            self.x_max_var.set("5")
            self.y_max_var.set("5")
        else:
            self.x_max_var.set("1")
            self.y_max_var.set("1")
        
        # 如果已有图片，刷新显示
        if self.current_image_path:
            self.refresh_plot()
            
    def upload_image(self):
        """上传图片"""
        file_path = filedialog.askopenfilename(
            title=language_manager.get('select_image', id=self.block_id),
            filetypes=[
                (language_manager.get('image_files'), "*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff"),
                ("TIFF", "*.tif *.tiff"),
                (language_manager.get('all_files'), "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image_path = file_path
                self.process_and_display_image()
                self.refresh_btn.config(state="normal")
                self.save_plot_btn.config(state="normal")
            except Exception as e:
                messagebox.showerror(
                    language_manager.get('error'), 
                    language_manager.get('process_image_error', error=str(e))
                )
                
    def process_and_display_image(self):
        """处理并显示图片"""
        try:
            # 获取参数
            color_space = self.color_space_var.get()
            
            # 验证降采样率
            try:
                sample_rate = int(self.sample_rate_var.get())
                if sample_rate < 1 or sample_rate > 1000:
                    raise ValueError()
            except ValueError:
                messagebox.showerror(
                    language_manager.get('error'),
                    language_manager.get('invalid_sample_rate')
                )
                return
            
            # 处理图片
            self.image_data = ImageProcessor.process_image(
                self.current_image_path,
                color_space,
                sample_rate
            )
            
            # 显示原图
            self.display_original_image()
            
            # 显示图片信息
            self.display_image_info()
            
            # 显示统计图
            self.display_plot()
            
        except Exception as e:
            raise Exception(language_manager.get('process_image_failed', error=str(e)))
            
    def display_original_image(self):
        """显示原始图片"""
        if self.image_data and 'original_image' in self.image_data:
            # 获取原图
            original = self.image_data['original_image']
            
            # 复制图像以避免修改原始数据
            display_image = original.copy()
            
            # 调整大小以适应显示区域
            display_size = (300, 300)
            display_image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(display_image)
            
            # 更新标签
            self.original_label.config(image=photo, text="")
            self.original_label.image = photo  # 保持引用
            
    def display_image_info(self):
        """显示图片信息"""
        if self.image_data and 'file_info' in self.image_data:
            file_info = self.image_data['file_info']
            self.filename_label.config(text=f"{language_manager.get('filename')} {file_info['filename']}")
            self.filesize_label.config(text=f"{language_manager.get('file_size')} {file_info['file_size']}")
            self.dimensions_label.config(text=f"{language_manager.get('dimensions')} {file_info['width']} x {file_info['height']} {language_manager.get('pixels')}")
            
    def display_plot(self):
        """显示统计图"""
        if not self.image_data:
            return
            
        # 清除旧图
        self.ax.clear()
        
        # 获取数据
        x_data = self.image_data['x_data']
        y_data = self.image_data['y_data']
        x_label = self.image_data['x_label']
        y_label = self.image_data['y_label']
        point_count = self.image_data['point_count']
        
        # 绘制散点图
        if len(x_data) > 0:
            # 获取用户设置的点大小
            try:
                user_point_size = float(self.point_size_var.get())
                if user_point_size <= 0:
                    user_point_size = 1.0
            except ValueError:
                user_point_size = 1.0
            
            # 根据数据点数量调整点的大小和透明度，并应用用户设置的缩放因子
            if point_count > 10000:
                size = 0.1 * user_point_size
                alpha = 0.3
            elif point_count > 5000:
                size = 0.5 * user_point_size
                alpha = 0.4
            elif point_count > 1000:
                size = 1 * user_point_size
                alpha = 0.5
            else:
                size = 2 * user_point_size
                alpha = 0.6
                
            # 使用用户自定义的颜色
            self.ax.scatter(x_data, y_data, s=size, alpha=alpha, c=self.plot_color)
            
        # 设置标签
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.grid(True, alpha=0.3)
        
        # 应用坐标轴范围
        self.apply_axis_range()
        
        # 刷新画布
        self.canvas.draw()
        
    def refresh_plot(self):
        """刷新统计图"""
        if self.current_image_path:
            self.process_and_display_image()
            
    def apply_axis_range(self):
        """应用坐标轴范围"""
        try:
            x_min = float(self.x_min_var.get())
            x_max = float(self.x_max_var.get())
            y_min = float(self.y_min_var.get())
            y_max = float(self.y_max_var.get())
            
            if x_min >= x_max or y_min >= y_max:
                messagebox.showwarning(
                    language_manager.get('warning'), 
                    language_manager.get('min_must_less_than_max')
                )
                return
                
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            self.canvas.draw()
            
        except ValueError:
            messagebox.showerror(
                language_manager.get('error'), 
                language_manager.get('please_enter_valid_number')
            )
            
    def auto_axis_range(self):
        """自动设置坐标轴范围"""
        if self.image_data:
            x_data = self.image_data['x_data']
            y_data = self.image_data['y_data']
            
            if len(x_data) > 0:
                x_min, x_max = np.min(x_data), np.max(x_data)
                y_min, y_max = np.min(y_data), np.max(y_data)
                
                # 添加10%的边距
                x_margin = (x_max - x_min) * 0.1
                y_margin = (y_max - y_min) * 0.1
                
                self.x_min_var.set(f"{x_min - x_margin:.2f}")
                self.x_max_var.set(f"{x_max + x_margin:.2f}")
                self.y_min_var.set(f"{y_min - y_margin:.2f}")
                self.y_max_var.set(f"{y_max + y_margin:.2f}")
                
                self.apply_axis_range()
    
    def save_plot(self):
        """保存当前图表到文件"""
        if not self.image_data:
            return
        
        try:
            # 生成默认文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"plot_block{self.block_id}_{timestamp}.png"
            
            # 打开文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title=language_manager.get('save_plot_title', id=self.block_id),
                defaultextension=".png",
                initialfile=default_filename,
                filetypes=[
                    ("PNG", "*.png"),
                    ("PDF", "*.pdf"),
                    ("SVG", "*.svg"),
                    ("EPS", "*.eps"),
                    (language_manager.get('all_files'), "*.*")
                ]
            )
            
            if file_path:
                # 获取文件扩展名
                _, ext = os.path.splitext(file_path)
                ext = ext.lower()
                
                # 设置DPI（对于PNG格式提高分辨率）
                dpi = 150 if ext == '.png' else 100
                
                # 保存图表
                self.figure.savefig(file_path, dpi=dpi, bbox_inches='tight')
                
                # 显示成功消息
                messagebox.showinfo(
                    language_manager.get('plot_saved'),
                    language_manager.get('plot_saved_to', path=file_path)
                )
                
        except Exception as e:
            messagebox.showerror(
                language_manager.get('error'),
                language_manager.get('save_plot_error', error=str(e))
            )
    
    def choose_color(self):
        """打开颜色选择对话框"""
        title = language_manager.get('select_block_color', id=self.block_id)
        new_color = pick_color(self, self.plot_color, title)
        
        if new_color:
            self.plot_color = new_color
            self.color_btn.config(fg=self.plot_color)
            
            # 如果已有图片，刷新显示
            if self.image_data:
                self.display_plot()