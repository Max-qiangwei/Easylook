"""
主窗口模块
管理2x2的图片块布局和模式切换
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modules.image_block import ImageBlock
from modules.comparison_mode import ComparisonMode
from modules.language_manager import language_manager


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        """
        初始化主窗口
        
        Args:
            root: Tk根窗口
        """
        self.root = root
        self.image_blocks = []
        self.current_mode = "multi_block"  # 当前模式
        self.multi_block_frame = None
        self.comparison_frame = None
        
        # 注册语言变化观察者
        language_manager.register_observer(self.update_language)
        
        self.setup_ui()
        self.setup_menu()
        self.update_title()
        
    def setup_ui(self):
        """设置UI布局"""
        # 创建主容器
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(expand=True, fill="both")
        
        # 先创建底部状态栏
        self.create_status_bar()
        
        # 检查屏幕大小，决定是否需要滚动条
        self.check_screen_size()
        
        # 然后初始化为多块模式
        self.show_multi_block_mode()
        
    def check_screen_size(self):
        """检查屏幕大小并调整布局"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 对于小屏幕（高度小于768或宽度小于1366），启用滚动支持
        self.use_scrollbar = screen_height < 768 or screen_width < 1366
        
    def show_multi_block_mode(self):
        """显示多块模式（2x2）"""
        # 隐藏对比模式（如果存在）
        if self.comparison_frame:
            self.comparison_frame.pack_forget()
        
        # 如果多块模式框架不存在，创建它
        if not self.multi_block_frame:
            if self.use_scrollbar:
                # 创建滚动画布和滚动条
                self.canvas = tk.Canvas(self.main_container)
                self.scrollbar_v = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
                self.scrollbar_h = ttk.Scrollbar(self.main_container, orient="horizontal", command=self.canvas.xview)
                self.scrollable_frame = ttk.Frame(self.canvas)
                
                self.scrollable_frame.bind(
                    "<Configure>",
                    lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                )
                
                self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
                self.canvas.configure(yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)
                
                # 绑定鼠标滚轮事件
                self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
                
                self.multi_block_frame = ttk.Frame(self.scrollable_frame)
            else:
                self.multi_block_frame = ttk.Frame(self.main_container)
            
            # 配置网格权重，使四个块均匀分布
            for i in range(2):
                self.multi_block_frame.grid_rowconfigure(i, weight=1)
                self.multi_block_frame.grid_columnconfigure(i, weight=1)
            
            # 创建2x2的图片块
            block_id = 1
            for row in range(2):
                for col in range(2):
                    # 创建分隔框架
                    separator_frame = ttk.Frame(self.multi_block_frame, relief="ridge", borderwidth=2)
                    separator_frame.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
                    
                    # 配置分隔框架的网格
                    separator_frame.grid_rowconfigure(0, weight=1)
                    separator_frame.grid_columnconfigure(0, weight=1)
                    
                    # 创建图片块
                    image_block = ImageBlock(separator_frame, block_id)
                    image_block.grid(row=0, column=0, sticky="nsew")
                    
                    self.image_blocks.append(image_block)
                    block_id += 1
        
        # 显示多块模式
        if self.use_scrollbar:
            self.multi_block_frame.pack(expand=True, fill="both", padx=5, pady=5)
            self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            self.scrollbar_v.pack(side="right", fill="y")
            self.scrollbar_h.pack(side="bottom", fill="x")
        else:
            self.multi_block_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.current_mode = "multi_block"
        self.update_status(language_manager.get('status_ready'))
    
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        if hasattr(self, 'canvas'):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def show_comparison_mode(self):
        """显示对比模式"""
        # 隐藏多块模式
        if self.multi_block_frame:
            self.multi_block_frame.pack_forget()
            # 如果有滚动条，也隐藏它们
            if hasattr(self, 'canvas'):
                self.canvas.pack_forget()
            if hasattr(self, 'scrollbar_v'):
                self.scrollbar_v.pack_forget()
            if hasattr(self, 'scrollbar_h'):
                self.scrollbar_h.pack_forget()
        
        # 如果对比模式框架不存在，创建它
        if not self.comparison_frame:
            self.comparison_frame = ComparisonMode(self.main_container)
        
        # 显示对比模式
        self.comparison_frame.pack(expand=True, fill="both", padx=10, pady=10)
        self.current_mode = "comparison"
        self.update_status(language_manager.get('comparison_mode_title'))
        
    def switch_to_multi_block(self):
        """切换到多块模式"""
        if self.current_mode != "multi_block":
            self.show_multi_block_mode()
            
    def switch_to_comparison(self):
        """切换到对比模式"""
        if self.current_mode != "comparison":
            self.show_comparison_mode()
        
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side="bottom", fill="x")
        
        # 分隔线
        separator = ttk.Separator(status_frame, orient="horizontal")
        separator.pack(side="top", fill="x")
        
        # 状态标签
        self.status_label = ttk.Label(
            status_frame,
            text=language_manager.get('status_ready'),
            relief="sunken",
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=5, pady=2)
        
        # 当前模式标签
        mode_text = language_manager.get('multi_block_mode')
        self.mode_status_label = ttk.Label(
            status_frame,
            text=f"Mode: {mode_text}",
            relief="sunken",
            anchor="center"
        )
        self.mode_status_label.pack(side="left", padx=5, pady=2)
        
        # 当前语言标签
        current_lang = "中文" if language_manager.get_current_language() == 'zh_CN' else "English"
        self.language_status_label = ttk.Label(
            status_frame,
            text=f"Language: {current_lang}",
            relief="sunken",
            anchor="center"
        )
        self.language_status_label.pack(side="left", padx=5, pady=2)
        
        # 版本信息
        self.version_label = ttk.Label(
            status_frame,
            text="v1.1.0",
            relief="sunken",
            anchor="e"
        )
        self.version_label.pack(side="right", padx=5, pady=2)
        
    def update_status(self, text):
        """更新状态栏文本"""
        self.status_label.config(text=text)
        
        # 更新模式显示
        if self.current_mode == "multi_block":
            mode_text = language_manager.get('multi_block_mode')
        else:
            mode_text = language_manager.get('comparison_mode')
        self.mode_status_label.config(text=f"Mode: {mode_text}")
        
    def setup_menu(self):
        """设置菜单栏"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # 文件菜单
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=language_manager.get('file_menu'), menu=self.file_menu)
        self.file_menu.add_command(
            label=language_manager.get('clear_all_blocks'), 
            command=self.clear_all_blocks
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label=language_manager.get('exit'), 
            command=self.root.quit
        )
        
        # 模式菜单
        self.mode_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=language_manager.get('mode_menu'), menu=self.mode_menu)
        
        # 添加模式选项，使用单选按钮样式
        self.mode_var = tk.StringVar(value="multi_block")
        self.mode_menu.add_radiobutton(
            label=language_manager.get('multi_block_mode'),
            variable=self.mode_var,
            value='multi_block',
            command=self.switch_to_multi_block
        )
        self.mode_menu.add_radiobutton(
            label=language_manager.get('comparison_mode'),
            variable=self.mode_var,
            value='comparison',
            command=self.switch_to_comparison
        )
        
        # 视图菜单
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=language_manager.get('view_menu'), menu=self.view_menu)
        self.view_menu.add_command(
            label=language_manager.get('refresh_all_plots'), 
            command=self.refresh_all_plots
        )
        self.view_menu.add_command(
            label=language_manager.get('auto_adjust_all_axes'), 
            command=self.auto_adjust_all_axes
        )
        
        # 语言菜单
        self.language_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=language_manager.get('language_menu'), menu=self.language_menu)
        
        # 添加语言选项，使用单选按钮样式
        self.language_var = tk.StringVar(value=language_manager.get_current_language())
        self.language_menu.add_radiobutton(
            label=language_manager.get('chinese'),
            variable=self.language_var,
            value='zh_CN',
            command=lambda: self.change_language('zh_CN')
        )
        self.language_menu.add_radiobutton(
            label=language_manager.get('english'),
            variable=self.language_var,
            value='en_US',
            command=lambda: self.change_language('en_US')
        )
        
        # 帮助菜单
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=language_manager.get('help_menu'), menu=self.help_menu)
        self.help_menu.add_command(
            label=language_manager.get('usage_help'), 
            command=self.show_help
        )
        self.help_menu.add_command(
            label=language_manager.get('about'), 
            command=self.show_about
        )
        
    def change_language(self, language_code):
        """
        切换语言
        
        Args:
            language_code: 语言代码 ('zh_CN' 或 'en_US')
        """
        language_manager.set_language(language_code)
        
    def update_language(self):
        """更新界面语言"""
        # 更新窗口标题
        self.update_title()
        
        # 更新菜单
        self.menubar.entryconfig(1, label=language_manager.get('file_menu'))
        self.menubar.entryconfig(2, label=language_manager.get('mode_menu'))
        self.menubar.entryconfig(3, label=language_manager.get('view_menu'))
        self.menubar.entryconfig(4, label=language_manager.get('language_menu'))
        self.menubar.entryconfig(5, label=language_manager.get('help_menu'))
        
        # 更新文件菜单项
        self.file_menu.entryconfig(0, label=language_manager.get('clear_all_blocks'))
        self.file_menu.entryconfig(2, label=language_manager.get('exit'))
        
        # 更新模式菜单项
        self.mode_menu.entryconfig(0, label=language_manager.get('multi_block_mode'))
        self.mode_menu.entryconfig(1, label=language_manager.get('comparison_mode'))
        
        # 更新视图菜单项
        self.view_menu.entryconfig(0, label=language_manager.get('refresh_all_plots'))
        self.view_menu.entryconfig(1, label=language_manager.get('auto_adjust_all_axes'))
        
        # 更新语言菜单项
        self.language_menu.entryconfig(0, label=language_manager.get('chinese'))
        self.language_menu.entryconfig(1, label=language_manager.get('english'))
        
        # 更新帮助菜单项
        self.help_menu.entryconfig(0, label=language_manager.get('usage_help'))
        self.help_menu.entryconfig(1, label=language_manager.get('about'))
        
        # 更新状态栏
        if self.current_mode == "multi_block":
            self.status_label.config(text=language_manager.get('status_ready'))
            mode_text = language_manager.get('multi_block_mode')
        else:
            self.status_label.config(text=language_manager.get('comparison_mode_title'))
            mode_text = language_manager.get('comparison_mode')
        
        self.mode_status_label.config(text=f"Mode: {mode_text}")
        
        # 更新语言状态
        current_lang = "中文" if language_manager.get_current_language() == 'zh_CN' else "English"
        self.language_status_label.config(text=f"Language: {current_lang}")
        
    def update_title(self):
        """更新窗口标题"""
        self.root.title(language_manager.get('app_title'))
        
    def clear_all_blocks(self):
        """清空所有图片块（仅在多块模式下有效）"""
        if self.current_mode != "multi_block":
            messagebox.showinfo(
                language_manager.get('info'),
                "此功能仅在多块模式下可用"
            )
            return
            
        result = messagebox.askyesno(
            language_manager.get('confirm'), 
            language_manager.get('confirm_clear_all')
        )
        if result:
            for block in self.image_blocks:
                # 重置每个块
                block.current_image_path = None
                block.image_data = None
                block.original_label.config(image="", text=language_manager.get('please_upload'))
                block.ax.clear()
                block.ax.set_xlabel('x')
                block.ax.set_ylabel('y')
                block.ax.grid(True, alpha=0.3)
                block.canvas.draw()
                block.refresh_btn.config(state="disabled")
                block.save_plot_btn.config(state="disabled")
                
                # 清空图片信息
                block.filename_label.config(text=language_manager.get('filename') + " -")
                block.filesize_label.config(text=language_manager.get('file_size') + " -")
                block.dimensions_label.config(text=language_manager.get('dimensions') + " -")
            
            self.status_label.config(text=language_manager.get('status_all_cleared'))
            
    def refresh_all_plots(self):
        """刷新所有统计图（仅在多块模式下有效）"""
        if self.current_mode != "multi_block":
            messagebox.showinfo(
                language_manager.get('info'),
                "此功能仅在多块模式下可用"
            )
            return
            
        refreshed_count = 0
        for block in self.image_blocks:
            if block.current_image_path:
                block.refresh_plot()
                refreshed_count += 1
        
        if refreshed_count > 0:
            self.status_label.config(text=language_manager.get('status_refreshed', count=refreshed_count))
        else:
            messagebox.showinfo(
                language_manager.get('info'), 
                language_manager.get('no_plots_to_refresh')
            )
            
    def auto_adjust_all_axes(self):
        """自动调整所有坐标轴范围（仅在多块模式下有效）"""
        if self.current_mode != "multi_block":
            messagebox.showinfo(
                language_manager.get('info'),
                "此功能仅在多块模式下可用"
            )
            return
            
        adjusted_count = 0
        for block in self.image_blocks:
            if block.image_data:
                block.auto_axis_range()
                adjusted_count += 1
        
        if adjusted_count > 0:
            self.status_label.config(text=language_manager.get('status_adjusted', count=adjusted_count))
        else:
            messagebox.showinfo(
                language_manager.get('info'), 
                language_manager.get('no_plots_to_adjust')
            )
            
    def show_help(self):
        """显示使用说明"""
        help_text = language_manager.get('help_text')
        
        # 添加对比模式的说明
        if language_manager.get_current_language() == 'zh_CN':
            help_text += """

6. 对比模式：
   - 模式菜单可切换到对比模式
   - 在单个图表中对比多张图片
   - 支持自定义降采样率（1-1000）
   - 每张图片用不同颜色显示
   - 可以逐个添加或移除图片"""
        else:
            help_text += """

6. Comparison Mode:
   - Switch to comparison mode from Mode menu
   - Compare multiple images in single plot
   - Support custom sample rate (1-1000)
   - Each image displayed in different color
   - Add or remove images individually"""
        
        messagebox.showinfo(
            language_manager.get('usage_help'), 
            help_text
        )
        
    def show_about(self):
        """显示关于信息"""
        about_text = language_manager.get('about_text')
        
        # 更新版本号
        about_text = about_text.replace("1.0.0", "1.1.0")
        
        messagebox.showinfo(
            language_manager.get('about'), 
            about_text
        )