#!/usr/bin/env python3
"""
图像颜色空间分析器
主程序入口
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.main_window import MainWindow

def main():
    """主函数"""
    root = tk.Tk()
    root.title("Easy Look")
    
    # 设置窗口大小和位置
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # 窗口大小为屏幕的80%
    window_width = int(screen_width * 0.9)
    window_height = int(screen_height * 0.9)
    
    # 居中显示
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2 - int(window_height * 0.05)
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.minsize(800, 600)
    
    # 创建主窗口
    app = MainWindow(root)
    
    # 运行主循环
    root.mainloop()

if __name__ == "__main__":
    main()