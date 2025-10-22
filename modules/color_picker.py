"""
颜色选择器对话框
允许用户通过色盘或RGB输入选择颜色
"""

import tkinter as tk
from tkinter import ttk, colorchooser
import colorsys
from modules.language_manager import language_manager


class ColorPicker(tk.Toplevel):
    """颜色选择器对话框"""
    
    def __init__(self, parent, initial_color='#0000FF', title=None):
        """
        初始化颜色选择器
        
        Args:
            parent: 父窗口
            initial_color: 初始颜色（十六进制格式）
            title: 窗口标题
        """
        super().__init__(parent)
        # 如果没有提供标题，使用默认标题
        if title is None:
            title = language_manager.get('select_color')
        self.title(title)
        self.geometry("400x550")  # 减小高度
        self.resizable(False, False)
        
        # 设置为模态对话框
        self.transient(parent)
        self.grab_set()
        
        # 结果变量
        self.result_color = None
        self.initial_color = initial_color
        
        # 将十六进制颜色转换为RGB
        self.current_rgb = self.hex_to_rgb(initial_color)
        
        self.setup_ui()
        
        # 设置初始颜色
        self.update_color_display()
        
        # 居中显示
        self.center_window()
        
    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        """设置UI布局"""
        # 主容器
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # 颜色显示区域
        display_frame = ttk.LabelFrame(main_frame, text=language_manager.get('current_color'), padding="10")
        display_frame.pack(fill="x", pady=(0, 10))
        
        self.color_display = tk.Canvas(display_frame, width=350, height=80, bg=self.initial_color)
        self.color_display.pack()
        
        # RGB输入区域
        rgb_frame = ttk.LabelFrame(main_frame, text=language_manager.get('rgb_values'), padding="10")
        rgb_frame.pack(fill="x", pady=(0, 10))
        
        # R值
        r_frame = ttk.Frame(rgb_frame)
        r_frame.pack(fill="x", pady=2)
        ttk.Label(r_frame, text="R:", width=3).pack(side="left", padx=(0, 5))
        self.r_var = tk.StringVar(value=str(self.current_rgb[0]))
        self.r_entry = ttk.Entry(r_frame, textvariable=self.r_var, width=10)
        self.r_entry.pack(side="left", padx=(0, 10))
        self.r_slider = ttk.Scale(r_frame, from_=0, to=255, orient="horizontal", 
                                   value=self.current_rgb[0], command=self.on_r_slider_change)
        self.r_slider.pack(side="left", fill="x", expand=True)
        
        # G值
        g_frame = ttk.Frame(rgb_frame)
        g_frame.pack(fill="x", pady=2)
        ttk.Label(g_frame, text="G:", width=3).pack(side="left", padx=(0, 5))
        self.g_var = tk.StringVar(value=str(self.current_rgb[1]))
        self.g_entry = ttk.Entry(g_frame, textvariable=self.g_var, width=10)
        self.g_entry.pack(side="left", padx=(0, 10))
        self.g_slider = ttk.Scale(g_frame, from_=0, to=255, orient="horizontal",
                                   value=self.current_rgb[1], command=self.on_g_slider_change)
        self.g_slider.pack(side="left", fill="x", expand=True)
        
        # B值
        b_frame = ttk.Frame(rgb_frame)
        b_frame.pack(fill="x", pady=2)
        ttk.Label(b_frame, text="B:", width=3).pack(side="left", padx=(0, 5))
        self.b_var = tk.StringVar(value=str(self.current_rgb[2]))
        self.b_entry = ttk.Entry(b_frame, textvariable=self.b_var, width=10)
        self.b_entry.pack(side="left", padx=(0, 10))
        self.b_slider = ttk.Scale(b_frame, from_=0, to=255, orient="horizontal",
                                   value=self.current_rgb[2], command=self.on_b_slider_change)
        self.b_slider.pack(side="left", fill="x", expand=True)
        
        # 绑定输入框事件
        self.r_entry.bind('<Return>', self.on_rgb_entry_change)
        self.g_entry.bind('<Return>', self.on_rgb_entry_change)
        self.b_entry.bind('<Return>', self.on_rgb_entry_change)
        self.r_entry.bind('<FocusOut>', self.on_rgb_entry_change)
        self.g_entry.bind('<FocusOut>', self.on_rgb_entry_change)
        self.b_entry.bind('<FocusOut>', self.on_rgb_entry_change)
        
        # 十六进制输入
        hex_frame = ttk.LabelFrame(main_frame, text=language_manager.get('hex_value'), padding="10")
        hex_frame.pack(fill="x", pady=(0, 10))
        
        hex_input_frame = ttk.Frame(hex_frame)
        hex_input_frame.pack(fill="x")
        ttk.Label(hex_input_frame, text="HEX:").pack(side="left", padx=(0, 5))
        self.hex_var = tk.StringVar(value=self.initial_color)
        self.hex_entry = ttk.Entry(hex_input_frame, textvariable=self.hex_var, width=15)
        self.hex_entry.pack(side="left", padx=(0, 10))
        self.hex_entry.bind('<Return>', self.on_hex_entry_change)
        self.hex_entry.bind('<FocusOut>', self.on_hex_entry_change)
        
        # 系统颜色选择器按钮
        ttk.Button(hex_input_frame, text=language_manager.get('system_color_picker'),
                  command=self.open_system_color_picker).pack(side="left")
        
        # 预设颜色
        preset_frame = ttk.LabelFrame(main_frame, text=language_manager.get('preset_colors'), padding="5")  # 减小内边距
        preset_frame.pack(fill="x", pady=(0, 10))
        
        preset_colors_frame = ttk.Frame(preset_frame)
        preset_colors_frame.pack()
        
        # 更好看的预设颜色列表
        preset_colors = [
            # 第一行：基础色彩
            '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#800080',
            # 第二行：柔和色彩
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
            # 第三行：深色和中性色
            '#2C3E50', '#34495E', '#7F8C8D', '#95A5A6', '#BDC3C7', '#ECF0F1', '#505050', '#000000'
        ]
        
        for i, color in enumerate(preset_colors):
            row = i // 8  # 每行8个颜色
            col = i % 8
            btn = tk.Button(preset_colors_frame, bg=color, width=5, height=1,  # 减小颜色块大小
                           command=lambda c=color: self.select_preset_color(c),
                           bd=0, relief="flat", highlightthickness=1, highlightbackground="#DDD")
            btn.grid(row=row, column=col, padx=1, pady=1)  # 减小间距
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text=language_manager.get('ok'), command=self.on_ok).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text=language_manager.get('cancel'), command=self.on_cancel).pack(side="right")
        ttk.Button(button_frame, text=language_manager.get('reset'), command=self.on_reset).pack(side="left")
        
    def hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, r, g, b):
        """将RGB转换为十六进制颜色"""
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def update_color_display(self):
        """更新颜色显示"""
        hex_color = self.rgb_to_hex(*self.current_rgb)
        self.color_display.config(bg=hex_color)
        self.hex_var.set(hex_color.upper())
        
    def on_r_slider_change(self, value):
        """R滑块变化事件"""
        r = int(float(value))
        self.current_rgb = (r, self.current_rgb[1], self.current_rgb[2])
        self.r_var.set(str(r))
        self.update_color_display()
        
    def on_g_slider_change(self, value):
        """G滑块变化事件"""
        g = int(float(value))
        self.current_rgb = (self.current_rgb[0], g, self.current_rgb[2])
        self.g_var.set(str(g))
        self.update_color_display()
        
    def on_b_slider_change(self, value):
        """B滑块变化事件"""
        b = int(float(value))
        self.current_rgb = (self.current_rgb[0], self.current_rgb[1], b)
        self.b_var.set(str(b))
        self.update_color_display()
        
    def on_rgb_entry_change(self, event=None):
        """RGB输入框变化事件"""
        try:
            r = int(self.r_var.get())
            g = int(self.g_var.get())
            b = int(self.b_var.get())
            
            # 限制范围
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            self.current_rgb = (r, g, b)
            
            # 更新滑块
            self.r_slider.set(r)
            self.g_slider.set(g)
            self.b_slider.set(b)
            
            # 更新显示
            self.update_color_display()
            
        except ValueError:
            pass
            
    def on_hex_entry_change(self, event=None):
        """十六进制输入框变化事件"""
        try:
            hex_value = self.hex_var.get().strip()
            if not hex_value.startswith('#'):
                hex_value = '#' + hex_value
                
            # 验证十六进制格式
            if len(hex_value) == 7:
                rgb = self.hex_to_rgb(hex_value)
                self.current_rgb = rgb
                
                # 更新RGB输入框
                self.r_var.set(str(rgb[0]))
                self.g_var.set(str(rgb[1]))
                self.b_var.set(str(rgb[2]))
                
                # 更新滑块
                self.r_slider.set(rgb[0])
                self.g_slider.set(rgb[1])
                self.b_slider.set(rgb[2])
                
                # 更新显示
                self.update_color_display()
                
        except:
            pass
            
    def select_preset_color(self, color):
        """选择预设颜色"""
        self.hex_var.set(color)
        self.on_hex_entry_change()
        
    def open_system_color_picker(self):
        """打开系统颜色选择器"""
        initial_color = self.rgb_to_hex(*self.current_rgb)
        color = colorchooser.askcolor(initialcolor=initial_color, parent=self)
        
        if color[1]:  # 如果选择了颜色
            self.hex_var.set(color[1])
            self.on_hex_entry_change()
            
    def on_reset(self):
        """重置到初始颜色"""
        self.hex_var.set(self.initial_color)
        self.on_hex_entry_change()
        
    def on_ok(self):
        """确定按钮"""
        self.result_color = self.rgb_to_hex(*self.current_rgb)
        self.destroy()
        
    def on_cancel(self):
        """取消按钮"""
        self.result_color = None
        self.destroy()
        
    def get_color(self):
        """获取选择的颜色"""
        return self.result_color


def pick_color(parent, initial_color='#0000FF', title=None):
    """
    显示颜色选择对话框并返回选择的颜色
    
    Args:
        parent: 父窗口
        initial_color: 初始颜色
        title: 窗口标题
        
    Returns:
        str: 选择的颜色（十六进制格式），如果取消则返回None
    """
    # 如果没有提供标题，使用默认标题
    if title is None:
        title = language_manager.get('select_color')
    dialog = ColorPicker(parent, initial_color, title)
    parent.wait_window(dialog)
    return dialog.get_color()