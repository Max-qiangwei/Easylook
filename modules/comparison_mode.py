"""
对比模式模块
允许在单个图表中对比多张图片
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


class ComparisonMode(ttk.Frame):
    """对比模式组件"""
    
    # 预定义的颜色列表（使用十六进制格式）
    COLORS = ['#0000FF', '#FF0000', '#008000', '#FFA500', '#800080', '#A52A2A', '#FFC0CB', '#808080', '#808000', '#00FFFF']
    
    # 颜色名称映射（用于matplotlib）
    COLOR_NAMES = {
        '#0000FF': 'blue',
        '#FF0000': 'red',
        '#008000': 'green',
        '#FFA500': 'orange',
        '#800080': 'purple',
        '#A52A2A': 'brown',
        '#FFC0CB': 'pink',
        '#808080': 'gray',
        '#808000': 'olive',
        '#00FFFF': 'cyan'
    }
    
    def __init__(self, parent, **kwargs):
        """
        初始化对比模式
        
        Args:
            parent: 父容器
        """
        super().__init__(parent, **kwargs)
        
        # 存储所有加载的图片数据
        self.image_data_list = []
        self.current_color_index = 0
        
        # 坐标轴范围
        self.x_min = 0
        self.x_max = 5
        self.y_min = 0
        self.y_max = 5
        
        # 默认点大小
        self.point_size = 1.0
        
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
        
        # 创建主显示区域
        self.create_main_display()
        
        # 创建坐标轴控制面板
        self.create_axis_control_panel()
        
    def create_control_panel(self):
        """创建顶部控制面板"""
        self.control_frame = ttk.LabelFrame(self, text=language_manager.get('control_panel'))
        self.control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 颜色空间选择
        self.color_space_label = ttk.Label(self.control_frame, text=language_manager.get('color_space'))
        self.color_space_label.grid(row=0, column=0, padx=5, pady=5)
        self.color_space_var = tk.StringVar(value="rg_bg")
        self.color_space_combo = ttk.Combobox(
            self.control_frame, 
            textvariable=self.color_space_var,
            values=["rg_bg", "chromaticity"],
            state="readonly",
            width=15
        )
        self.color_space_combo.grid(row=0, column=1, padx=5, pady=5)
        self.color_space_combo.bind('<<ComboboxSelected>>', self.on_color_space_change)
        
        # 自定义降采样率输入
        self.sample_rate_label = ttk.Label(self.control_frame, text=language_manager.get('custom_sample_rate'))
        self.sample_rate_label.grid(row=0, column=2, padx=5, pady=5)
        self.sample_rate_var = tk.StringVar(value="10")
        self.sample_rate_entry = ttk.Entry(self.control_frame, textvariable=self.sample_rate_var, width=8)
        self.sample_rate_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # 点大小控制
        self.point_size_label = ttk.Label(self.control_frame, text=language_manager.get('point_size'))
        self.point_size_label.grid(row=0, column=4, padx=5, pady=5)
        self.point_size_var = tk.StringVar(value="1.0")
        self.point_size_entry = ttk.Entry(self.control_frame, textvariable=self.point_size_var, width=8)
        self.point_size_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # 添加图片按钮
        self.add_image_btn = ttk.Button(
            self.control_frame,
            text=language_manager.get('add_image'),
            command=self.add_image
        )
        self.add_image_btn.grid(row=0, column=6, padx=5, pady=5)
        
        # 清空所有按钮
        self.clear_all_btn = ttk.Button(
            self.control_frame,
            text=language_manager.get('clear_all'),
            command=self.clear_all_images
        )
        self.clear_all_btn.grid(row=0, column=7, padx=5, pady=5)
        
        # 保存图表按钮
        self.save_plot_btn = ttk.Button(
            self.control_frame,
            text=language_manager.get('save_plot'),
            command=self.save_plot,
            state="disabled"
        )
        self.save_plot_btn.grid(row=0, column=8, padx=5, pady=5)
        
    def create_main_display(self):
        """创建主显示区域"""
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # 配置网格权重
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        
        # 左侧：图片列表
        self.create_image_list_panel(main_frame)
        
        # 右侧：统计图
        self.create_plot_panel(main_frame)
        
    def create_image_list_panel(self, parent):
        """创建图片列表面板"""
        list_frame = ttk.LabelFrame(parent, text=language_manager.get('image_list'))
        list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 创建滚动区域
        scroll_canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=scroll_canvas.yview)
        self.scrollable_frame = ttk.Frame(scroll_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )
        
        scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        
        scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.image_items_frame = self.scrollable_frame
        
    def create_plot_panel(self, parent):
        """创建统计图面板"""
        plot_frame = ttk.LabelFrame(parent, text=language_manager.get('color_distribution'))
        plot_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # 创建matplotlib图形
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.12)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.grid(True, alpha=0.3)
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.figure, plot_frame)
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
        
        # 自动范围按钮
        self.auto_btn = ttk.Button(
            self.axis_frame,
            text=language_manager.get('auto_range'),
            command=self.auto_axis_range
        )
        self.auto_btn.grid(row=0, column=11, padx=5, pady=5)
        
    def add_image(self):
        """添加新图片"""
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
        
        # 选择图片文件
        file_path = filedialog.askopenfilename(
            title=language_manager.get('select_image', id=''),
            filetypes=[
                (language_manager.get('image_files'), "*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff"),
                ("TIFF", "*.tif *.tiff"),
                (language_manager.get('all_files'), "*.*")
            ]
        )
        
        if file_path:
            try:
                # 处理图片
                color_space = self.color_space_var.get()
                image_data = ImageProcessor.process_image(file_path, color_space, sample_rate)
                
                # 分配颜色
                color = self.COLORS[self.current_color_index % len(self.COLORS)]
                self.current_color_index += 1
                
                # 添加到数据列表
                image_data['color'] = color
                image_data['path'] = file_path
                image_data['sample_rate'] = sample_rate  # 添加降采样率信息
                self.image_data_list.append(image_data)
                
                # 添加到界面列表
                self.add_image_item(image_data)
                
                # 更新图表
                self.update_plot()
                
                # 启用保存按钮
                if len(self.image_data_list) > 0:
                    self.save_plot_btn.config(state="normal")
                    
            except Exception as e:
                messagebox.showerror(
                    language_manager.get('error'),
                    language_manager.get('process_image_error', error=str(e))
                )
                
    def add_image_item(self, image_data):
        """添加图片项到列表"""
        item_frame = ttk.Frame(self.image_items_frame)
        item_frame.pack(fill="x", padx=5, pady=2)
        
        # 颜色标签（可点击修改颜色）
        color_btn = tk.Button(
            item_frame,
            text="■",
            fg=image_data['color'],
            font=("Arial", 16),
            bd=0,  # 去除边框
            relief="flat",  # 平坦样式
            command=lambda: self.change_image_color(image_data, color_btn),
            width=2,
            highlightthickness=0  # 去除高亮边框
        )
        color_btn.pack(side="left", padx=5)
        
        # 保存按钮引用
        image_data['color_btn'] = color_btn
        
        # 缩略图
        if 'original_image' in image_data:
            thumbnail = image_data['original_image'].copy()
            thumbnail.thumbnail((60, 60), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(thumbnail)
            thumbnail_label = ttk.Label(item_frame, image=photo)
            thumbnail_label.image = photo  # 保持引用
            thumbnail_label.pack(side="left", padx=5)
        
        # 文件信息
        file_info = image_data['file_info']
        sample_rate = image_data.get('sample_rate', 'N/A')  # 获取降采样率
        info_text = f"{file_info['filename']}\n{file_info['file_size']} | {file_info['width']}x{file_info['height']}\n{language_manager.get('downsample')}: 1/{sample_rate}"
        info_label = ttk.Label(item_frame, text=info_text)
        info_label.pack(side="left", padx=5, expand=True, fill="x")
        
        # 移除按钮
        remove_btn = ttk.Button(
            item_frame,
            text=language_manager.get('remove'),
            command=lambda: self.remove_image(image_data, item_frame)
        )
        remove_btn.pack(side="right", padx=5)
        
        # 保存框架引用
        image_data['item_frame'] = item_frame
        
    def remove_image(self, image_data, item_frame):
        """移除图片"""
        # 从列表中移除
        self.image_data_list.remove(image_data)
        
        # 从界面移除
        item_frame.destroy()
        
        # 更新图表
        self.update_plot()
        
        # 如果没有图片了，禁用保存按钮
        if len(self.image_data_list) == 0:
            self.save_plot_btn.config(state="disabled")
            
    def clear_all_images(self):
        """清空所有图片"""
        if len(self.image_data_list) == 0:
            return
            
        result = messagebox.askyesno(
            language_manager.get('confirm'),
            language_manager.get('confirm_clear_all')
        )
        
        if result:
            # 清空数据列表
            self.image_data_list.clear()
            self.current_color_index = 0
            
            # 清空界面列表
            for widget in self.image_items_frame.winfo_children():
                widget.destroy()
            
            # 清空图表
            self.ax.clear()
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.grid(True, alpha=0.3)
            self.canvas.draw()
            
            # 禁用保存按钮
            self.save_plot_btn.config(state="disabled")
            
    def update_plot(self):
        """更新统计图"""
        # 清除旧图
        self.ax.clear()
        
        # 获取用户设置的点大小
        try:
            user_point_size = float(self.point_size_var.get())
            if user_point_size <= 0:
                user_point_size = 1.0
        except ValueError:
            user_point_size = 1.0
        
        # 绘制所有数据集
        for image_data in self.image_data_list:
            x_data = image_data['x_data']
            y_data = image_data['y_data']
            color = image_data['color']
            filename = image_data['file_info']['filename']
            point_count = image_data['point_count']
            
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
            
            # 绘制散点图（将十六进制颜色转换为matplotlib可识别的格式）
            plot_color = self.COLOR_NAMES.get(color, color)  # 如果是预定义颜色使用名称，否则使用原始值
            self.ax.scatter(x_data, y_data, s=size, alpha=alpha, c=plot_color, label=filename)
        
        # 设置标签和图例
        if len(self.image_data_list) > 0:
            x_label = self.image_data_list[0]['x_label']
            y_label = self.image_data_list[0]['y_label']
            self.ax.set_xlabel(x_label)
            self.ax.set_ylabel(y_label)
            
            # 添加图例
            if len(self.image_data_list) > 1:
                self.ax.legend(loc='best', fontsize='small')
        else:
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
        
        self.ax.grid(True, alpha=0.3)
        
        # 应用坐标轴范围
        self.apply_axis_range()
        
        # 刷新画布
        self.canvas.draw()
        
    def on_color_space_change(self, event=None):
        """颜色空间变化事件"""
        if self.color_space_var.get() == "rg_bg":
            self.x_max_var.set("5")
            self.y_max_var.set("5")
        else:
            self.x_max_var.set("1")
            self.y_max_var.set("1")
        
        # 如果有图片，重新处理并更新
        if len(self.image_data_list) > 0:
            result = messagebox.askyesno(
                language_manager.get('confirm'),
                "切换颜色空间将重新处理所有图片，是否继续？"
            )
            if result:
                self.reprocess_all_images()
                
    def reprocess_all_images(self):
        """重新处理所有图片"""
        color_space = self.color_space_var.get()
        
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
        
        for image_data in self.image_data_list:
            try:
                # 重新处理图片
                file_path = image_data['path']
                new_data = ImageProcessor.process_image(file_path, color_space, sample_rate)
                
                # 更新数据，保留颜色和路径
                image_data.update(new_data)
                
            except Exception as e:
                messagebox.showerror(
                    language_manager.get('error'),
                    f"处理 {os.path.basename(file_path)} 时出错: {str(e)}"
                )
        
        # 更新图表
        self.update_plot()
        
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
        if len(self.image_data_list) == 0:
            return
        
        # 合并所有数据
        all_x_data = []
        all_y_data = []
        
        for image_data in self.image_data_list:
            all_x_data.extend(image_data['x_data'])
            all_y_data.extend(image_data['y_data'])
        
        if len(all_x_data) > 0:
            x_min, x_max = np.min(all_x_data), np.max(all_x_data)
            y_min, y_max = np.min(all_y_data), np.max(all_y_data)
            
            # 添加10%的边距
            x_margin = (x_max - x_min) * 0.1
            y_margin = (y_max - y_min) * 0.1
            
            self.x_min_var.set(f"{x_min - x_margin:.2f}")
            self.x_max_var.set(f"{x_max + x_margin:.2f}")
            self.y_min_var.set(f"{y_min - y_margin:.2f}")
            self.y_max_var.set(f"{y_max + y_margin:.2f}")
            
            self.apply_axis_range()
            
    def save_plot(self):
        """保存图表"""
        if len(self.image_data_list) == 0:
            return
        
        try:
            # 生成默认文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"comparison_plot_{timestamp}.png"
            
            # 打开文件保存对话框
            file_path = filedialog.asksaveasfilename(
                title=language_manager.get('save_plot_title', id='Comparison'),
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
                
                # 设置DPI
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
    
    def change_image_color(self, image_data, color_btn):
        """修改图片的显示颜色"""
        current_color = image_data['color']
        filename = image_data['file_info']['filename']
        
        # 打开颜色选择对话框
        title = language_manager.get('select_image_color', filename=filename)
        new_color = pick_color(self, current_color, title)
        
        if new_color:
            # 更新颜色（确保是十六进制格式）
            image_data['color'] = new_color
            color_btn.config(fg=new_color)
            
            # 刷新图表
            self.update_plot()
            
    def update_language(self):
        """更新界面语言"""
        # 更新控制面板
        self.control_frame.config(text=language_manager.get('control_panel'))
        self.color_space_label.config(text=language_manager.get('color_space'))
        self.sample_rate_label.config(text=language_manager.get('custom_sample_rate'))
        self.point_size_label.config(text=language_manager.get('point_size'))
        self.add_image_btn.config(text=language_manager.get('add_image'))
        self.clear_all_btn.config(text=language_manager.get('clear_all'))
        self.save_plot_btn.config(text=language_manager.get('save_plot'))
        
        # 更新坐标轴控制面板
        self.axis_frame.config(text=language_manager.get('axis_control'))
        self.x_axis_label.config(text=language_manager.get('x_axis_range'))
        self.y_axis_label.config(text=language_manager.get('y_axis_range'))
        self.x_min_label.config(text=language_manager.get('min_value'))
        self.x_max_label.config(text=language_manager.get('max_value'))
        self.y_min_label.config(text=language_manager.get('min_value'))
        self.y_max_label.config(text=language_manager.get('max_value'))
        self.apply_btn.config(text=language_manager.get('apply_range'))
        self.auto_btn.config(text=language_manager.get('auto_range'))