"""
语言管理模块
处理应用的多语言支持
"""

class LanguageManager:
    """语言管理器"""
    
    # 语言字典
    LANGUAGES = {
        'zh_CN': {
            # 主窗口
            'app_title': 'Easy Look',
            'file_menu': '文件',
            'view_menu': '视图',
            'help_menu': '帮助',
            'language_menu': '语言',
            'clear_all_blocks': '清空所有块',
            'exit': '退出',
            'refresh_all_plots': '刷新所有统计图',
            'auto_adjust_all_axes': '自动调整所有坐标轴',
            'usage_help': '使用说明',
            'about': '关于',
            'chinese': '中文',
            'english': 'English',
            'mode_menu': '模式',
            'multi_block_mode': '单图展示',
            'comparison_mode': '对比模式',
            
            # 状态栏
            'status_ready': '就绪 - 请在每个块中上传图片进行分析',
            'status_all_cleared': '所有图片块已清空',
            'status_refreshed': '已刷新 {count} 个统计图',
            'status_adjusted': '已自动调整 {count} 个图的坐标轴',
            
            # 图片块
            'image_block': '图片块',
            'control_panel': '控制面板',
            'color_space': '颜色空间:',
            'sample_rate': '降采样率:',
            'upload_image': '上传图片',
            'refresh_plot': '刷新统计图',
            'original_image': '原始图片',
            'color_distribution': '颜色空间统计图',
            'axis_control': '坐标轴范围控制',
            'x_axis_range': 'X轴范围:',
            'y_axis_range': 'Y轴范围:',
            'min_value': '最小值:',
            'max_value': '最大值:',
            'apply_range': '应用范围',
            'auto_range': '自动范围',
            'save_plot': '保存图表',
            'please_upload': '请上传图片',
            'add_image': '添加图片',
            'clear_all': '清空所有',
            'custom_sample_rate': '自定义降采样率:',
            'image_list': '图片列表',
            'remove': '移除',
            'downsample': '降采样',
            'point_size': '点大小:',
            
            # 颜色选择器
            'select_color': '选择颜色',
            'current_color': '当前颜色',
            'rgb_values': 'RGB值',
            'hex_value': '十六进制值',
            'preset_colors': '预设颜色',
            'system_color_picker': '选择颜色...',
            'ok': '确定',
            'cancel': '取消',
            'reset': '重置',
            'select_block_color': '选择块 {id} 的颜色',
            'select_image_color': '选择 {filename} 的颜色',
            
            # 图片信息
            'image_info': '图片信息',
            'filename': '文件名:',
            'file_size': '文件大小:',
            'dimensions': '尺寸:',
            'pixels': '像素',
            
            # 颜色空间选项
            'rg_bg_space': '(r/g, b/g空间)',
            'chromaticity_space': '(r/(r+g+b), g/(r+g+b)空间)',
            
            # 图表标签
            'color_distribution_title': '颜色空间分布 (采样点数: {count})',
            
            # 对话框
            'select_image': '选择图片 - 块{id}',
            'image_files': '图片文件',
            'all_files': '所有文件',
            'error': '错误',
            'warning': '警告',
            'info': '提示',
            'confirm': '确认',
            'confirm_clear_all': '确定要清空所有图片块吗？',
            'no_plots_to_refresh': '没有可刷新的统计图',
            'no_plots_to_adjust': '没有可调整的统计图',
            'min_must_less_than_max': '最小值必须小于最大值',
            'please_enter_valid_number': '请输入有效的数字',
            'process_image_error': '处理图片时出错:\n{error}',
            'process_image_failed': '处理图片失败: {error}',
            'cannot_load_image': '无法加载图像: {error}',
            'save_plot_title': '保存图表 - 块{id}',
            'plot_files': '图表文件',
            'plot_saved': '图表已保存',
            'plot_saved_to': '图表已保存到: {path}',
            'save_plot_error': '保存图表时出错: {error}',
            'enter_sample_rate': '请输入降采样率 (1-1000):',
            'invalid_sample_rate': '无效的降采样率，请输入1-1000之间的整数',
            'comparison_mode_title': '图像颜色空间对比分析',
            
            # 帮助文本
            'help_text': """图像颜色空间分析器 使用说明

1. 基本功能：
   - 应用程序分为2x2共4个独立的图片分析块
   - 每个块可以独立上传和分析图片
   - 左侧显示原始图片，右侧显示颜色空间统计图

2. 颜色空间选择：
   - r/g, b/g空间：将RGB值转换为r/g和b/g的比值
   - 色度空间：将RGB转换为r/(r+g+b)和g/(r+g+b)

3. 降采样率：
   - 控制统计图中显示的像素点数量
   - 数值越大，采样点越少，处理速度越快
   - 建议大图片使用较高的降采样率

4. 坐标轴控制：
   - 可手动输入坐标轴范围
   - "应用范围"按钮应用自定义范围
   - "自动范围"按钮自动计算最佳显示范围

5. 快捷操作：
   - 文件菜单可清空所有块
   - 视图菜单可批量刷新和调整坐标轴

提示：
- 支持常见图片格式(JPG, PNG, BMP等)
- 每个块独立工作，互不影响
- 可以对比不同图片在相同颜色空间的分布""",
            
            'about_text': """图像颜色空间分析器
版本：1.0.0

功能特点：
• 2x2四块独立分析区域
• 支持多种颜色空间转换
• 可调节降采样率
• 动态坐标轴范围控制
• 直观的散点图显示
• 多语言支持（中英文）

作者：AI Assistant
创建日期：2024"""
        },
        
        'en_US': {
            # Main window
            'app_title': 'Easy Look',
            'file_menu': 'File',
            'view_menu': 'View',
            'help_menu': 'Help',
            'language_menu': 'Language',
            'clear_all_blocks': 'Clear All Blocks',
            'exit': 'Exit',
            'refresh_all_plots': 'Refresh All Plots',
            'auto_adjust_all_axes': 'Auto Adjust All Axes',
            'usage_help': 'Usage Help',
            'about': 'About',
            'chinese': '中文',
            'english': 'English',
            'mode_menu': 'Mode',
            'multi_block_mode': 'Single Image Display',
            'comparison_mode': 'Comparison Mode',
            
            # Status bar
            'status_ready': 'Ready - Please upload images in each block for analysis',
            'status_all_cleared': 'All image blocks cleared',
            'status_refreshed': 'Refreshed {count} plot(s)',
            'status_adjusted': 'Auto adjusted {count} plot(s)',
            
            # Image block
            'image_block': 'Image Block',
            'control_panel': 'Control Panel',
            'color_space': 'Color Space:',
            'sample_rate': 'Sample Rate:',
            'upload_image': 'Upload Image',
            'refresh_plot': 'Refresh Plot',
            'original_image': 'Original Image',
            'color_distribution': 'Color Space Distribution',
            'axis_control': 'Axis Range Control',
            'x_axis_range': 'X-Axis Range:',
            'y_axis_range': 'Y-Axis Range:',
            'min_value': 'Min:',
            'max_value': 'Max:',
            'apply_range': 'Apply Range',
            'auto_range': 'Auto Range',
            'save_plot': 'Save Plot',
            'please_upload': 'Please upload an image',
            'add_image': 'Add Image',
            'clear_all': 'Clear All',
            'custom_sample_rate': 'Custom Sample Rate:',
            'image_list': 'Image List',
            'remove': 'Remove',
            'downsample': 'Downsample',
            'point_size': 'Point Size:',
            
            # Color picker
            'select_color': 'Select Color',
            'current_color': 'Current Color',
            'rgb_values': 'RGB Values',
            'hex_value': 'Hexadecimal',
            'preset_colors': 'Preset Colors',
            'system_color_picker': 'Choose Color...',
            'ok': 'OK',
            'cancel': 'Cancel',
            'reset': 'Reset',
            'select_block_color': 'Select Color for Block {id}',
            'select_image_color': 'Select Color for {filename}',
            
            # Image info
            'image_info': 'Image Info',
            'filename': 'Filename:',
            'file_size': 'File Size:',
            'dimensions': 'Dimensions:',
            'pixels': 'pixels',
            
            # Color space options
            'rg_bg_space': '(r/g, b/g space)',
            'chromaticity_space': '(r/(r+g+b), g/(r+g+b) space)',
            
            # Chart labels
            'color_distribution_title': 'Color Space Distribution (Points: {count})',
            
            # Dialogs
            'select_image': 'Select Image - Block {id}',
            'image_files': 'Image Files',
            'all_files': 'All Files',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Info',
            'confirm': 'Confirm',
            'confirm_clear_all': 'Are you sure you want to clear all image blocks?',
            'no_plots_to_refresh': 'No plots to refresh',
            'no_plots_to_adjust': 'No plots to adjust',
            'min_must_less_than_max': 'Minimum must be less than maximum',
            'please_enter_valid_number': 'Please enter a valid number',
            'process_image_error': 'Error processing image:\n{error}',
            'process_image_failed': 'Failed to process image: {error}',
            'cannot_load_image': 'Cannot load image: {error}',
            'save_plot_title': 'Save Plot - Block {id}',
            'plot_files': 'Plot Files',
            'plot_saved': 'Plot Saved',
            'plot_saved_to': 'Plot saved to: {path}',
            'save_plot_error': 'Error saving plot: {error}',
            'enter_sample_rate': 'Enter sample rate (1-1000):',
            'invalid_sample_rate': 'Invalid sample rate, please enter an integer between 1-1000',
            'comparison_mode_title': 'Image Color Space Comparison Analysis',
            
            # Help text
            'help_text': """Image Color Space Analyzer Usage

1. Basic Features:
   - Application has 2x2 independent image analysis blocks
   - Each block can upload and analyze images independently
   - Left side shows original image, right side shows color space plot

2. Color Space Selection:
   - r/g, b/g space: Converts RGB values to r/g and b/g ratios
   - Chromaticity space: Converts RGB to r/(r+g+b) and g/(r+g+b)

3. Sample Rate:
   - Controls number of pixels displayed in plot
   - Higher values mean fewer samples, faster processing
   - Recommended to use higher sample rate for large images

4. Axis Control:
   - Manually input axis ranges
   - "Apply Range" button applies custom range
   - "Auto Range" button calculates optimal display range

5. Quick Operations:
   - File menu can clear all blocks
   - View menu for batch refresh and axis adjustment

Tips:
- Supports common image formats (JPG, PNG, BMP, etc.)
- Each block works independently
- Compare different images in same color space""",
            
            'about_text': """Image Color Space Analyzer
Version: 1.0.0

Features:
• 2x2 independent analysis areas
• Multiple color space conversions
• Adjustable sample rate
• Dynamic axis range control
• Intuitive scatter plot display
• Multi-language support (Chinese/English)

Author: AI Assistant
Created: 2024"""
        }
    }
    
    def __init__(self, language='zh_CN'):
        """
        初始化语言管理器
        
        Args:
            language: 初始语言代码 ('zh_CN' 或 'en_US')
        """
        self.current_language = language
        self.observers = []
        
    def get(self, key, **kwargs):
        """
        获取当前语言的文本
        
        Args:
            key: 文本键
            **kwargs: 格式化参数
            
        Returns:
            str: 格式化后的文本
        """
        text = self.LANGUAGES.get(self.current_language, {}).get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text
        
    def set_language(self, language):
        """
        设置当前语言
        
        Args:
            language: 语言代码 ('zh_CN' 或 'en_US')
        """
        if language in self.LANGUAGES:
            self.current_language = language
            self.notify_observers()
            
    def register_observer(self, callback):
        """
        注册语言变化观察者
        
        Args:
            callback: 回调函数
        """
        self.observers.append(callback)
        
    def notify_observers(self):
        """通知所有观察者语言已改变"""
        for callback in self.observers:
            callback()
            
    def get_current_language(self):
        """获取当前语言代码"""
        return self.current_language


# 全局语言管理器实例
language_manager = LanguageManager('zh_CN')