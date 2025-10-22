"""
图像处理核心模块
负责颜色空间转换和降采样
"""

import numpy as np
from PIL import Image
import warnings
import os
import imageio.v3 as iio

class ImageProcessor:
    """图像处理器类"""
    
    @staticmethod
    def load_image(image_path):
        """
        加载图像并转换为RGB格式
        支持常见格式（JPEG, PNG等）以及TIFF格式（包括16位TIFF）
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            PIL.Image: RGB格式的图像对象
        """
        try:
            # 获取文件扩展名
            file_ext = os.path.splitext(image_path)[1].lower()
            
            # 对于TIFF格式，使用imageio读取以获得更好的兼容性
            if file_ext in ['.tif', '.tiff']:
                # 使用imageio读取TIFF图像
                img_array = iio.imread(image_path)
                
                # 保存原始数组的副本
                original_array = img_array.copy()
                
                # 先处理通道问题
                # 如果是多通道TIFF（如4通道RGBA），只取前3个通道
                if img_array.ndim == 3 and img_array.shape[2] > 3:
                    img_array = img_array[:, :, :3]
                    original_array = original_array[:, :, :3]
                # 如果是单通道灰度图，转换为3通道
                elif img_array.ndim == 2:
                    img_array = np.stack([img_array] * 3, axis=-1)
                    original_array = np.stack([original_array] * 3, axis=-1)
                
                # 检查数据类型和位深度，并归一化到0-255范围用于显示
                if img_array.dtype == np.uint16:
                    # 16位图像，归一化到0-255范围用于显示
                    # 对于显示：使用实际的最小最大值进行归一化，确保图像可见
                    max_val = img_array.max()
                    min_val = img_array.min()
                    
                    if max_val > min_val:
                        # 使用实际范围进行归一化以获得更好的显示效果
                        img_array_float = (img_array.astype(np.float64) - min_val) / (max_val - min_val)
                        img_array_display = (img_array_float * 255).astype(np.uint8)
                    else:
                        # 如果所有像素值相同，设置为中等灰度
                        img_array_display = np.full_like(img_array, 128, dtype=np.uint8)
                elif img_array.dtype == np.float32 or img_array.dtype == np.float64:
                    # 浮点图像，假设范围是0-1，转换到0-255
                    img_array_display = (np.clip(img_array, 0, 1) * 255).astype(np.uint8)
                elif img_array.dtype == np.uint8:
                    img_array_display = img_array
                else:
                    # 其他数据类型，尝试转换
                    # 先归一化到0-1范围，然后转换到0-255
                    min_val = img_array.min()
                    max_val = img_array.max()
                    if max_val > min_val:
                        img_array_display = ((img_array - min_val) / (max_val - min_val) * 255).astype(np.uint8)
                    else:
                        img_array_display = np.zeros_like(img_array, dtype=np.uint8)
                
                # 将numpy数组转换为PIL Image用于显示
                img = Image.fromarray(img_array_display)
                
                # 确保是RGB格式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 保存原始数据作为属性
                img.original_array = original_array
                img.is_16bit = (original_array.dtype == np.uint16)
            else:
                # 对于其他格式，使用PIL直接读取
                img = Image.open(image_path)
                # 确保是RGB格式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
            
            return img
        except Exception as e:
            raise Exception(f"无法加载图像: {str(e)}")
    
    @staticmethod
    def downsample_image(image, sample_rate):
        """
        对图像进行降采样
        
        Args:
            image: PIL.Image对象
            sample_rate: 降采样率 (1表示不降采样, 2表示每2个像素取1个, 等等)
            
        Returns:
            numpy.ndarray: 降采样后的RGB数组
        """
        # 检查是否有原始高精度数据
        if hasattr(image, 'original_array'):
            img_array = image.original_array
        else:
            # 转换为numpy数组
            img_array = np.array(image)
        
        # 降采样
        if sample_rate > 1:
            # 使用步长进行降采样
            if img_array.ndim == 3:
                sampled = img_array[::sample_rate, ::sample_rate, :]
            else:
                sampled = img_array[::sample_rate, ::sample_rate]
        else:
            sampled = img_array
            
        return sampled
    
    @staticmethod
    def convert_to_normalized_rg(rgb_array):
        """
        将RGB数组转换为归一化的r/g, b/g空间
        
        Args:
            rgb_array: RGB数组 (H, W, 3)
            
        Returns:
            tuple: (r/g值数组, b/g值数组, 有效像素掩码)
        """
        # 处理不同的数组形状
        if rgb_array.ndim == 2:
            # 单通道图像，复制为3通道
            rgb_array = np.stack([rgb_array] * 3, axis=-1)
        
        # 提取RGB通道，处理16位图像
        if rgb_array.dtype == np.uint16:
            # 16位图像，归一化到0-1范围
            # 对于颜色空间计算，使用标准的归一化方法（除以理论最大值）
            r = rgb_array[:, :, 0].astype(np.float64) / (2**16 - 1)
            g = rgb_array[:, :, 1].astype(np.float64) / (2**16 - 1)
            b = rgb_array[:, :, 2].astype(np.float64) / (2**16 - 1)
        else:
            # 8位图像或已归一化的图像
            r = rgb_array[:, :, 0].astype(np.float32)
            g = rgb_array[:, :, 1].astype(np.float32)
            b = rgb_array[:, :, 2].astype(np.float32)
            
            # 如果是8位图像，归一化到0-1范围
            if rgb_array.dtype == np.uint8:
                r = r / 255.0
                g = g / 255.0
                b = b / 255.0
        
        # 避免除零，找出g不为0的像素
        valid_mask = g > 0
        
        # 初始化结果数组
        rg = np.zeros_like(r)
        bg = np.zeros_like(b)
        
        # 计算r/g和b/g
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            rg[valid_mask] = r[valid_mask] / g[valid_mask]
            bg[valid_mask] = b[valid_mask] / g[valid_mask]
        
        return rg.flatten(), bg.flatten(), valid_mask.flatten()
    
    @staticmethod
    def convert_to_chromaticity(rgb_array):
        """
        将RGB数组转换为色度坐标 r/(r+g+b), g/(r+g+b)
        
        Args:
            rgb_array: RGB数组 (H, W, 3)
            
        Returns:
            tuple: (r/(r+g+b)值数组, g/(r+g+b)值数组, 有效像素掩码)
        """
        # 处理不同的数组形状
        if rgb_array.ndim == 2:
            # 单通道图像，复制为3通道
            rgb_array = np.stack([rgb_array] * 3, axis=-1)
        
        # 提取RGB通道，处理16位图像
        if rgb_array.dtype == np.uint16:
            # 16位图像，归一化到0-1范围
            # 对于颜色空间计算，使用标准的归一化方法（除以理论最大值）
            r = rgb_array[:, :, 0].astype(np.float64) / (2**16 - 1)
            g = rgb_array[:, :, 1].astype(np.float64) / (2**16 - 1)
            b = rgb_array[:, :, 2].astype(np.float64) / (2**16 - 1)
        else:
            # 8位图像或已归一化的图像
            r = rgb_array[:, :, 0].astype(np.float32)
            g = rgb_array[:, :, 1].astype(np.float32)
            b = rgb_array[:, :, 2].astype(np.float32)
            
            # 如果是8位图像，归一化到0-1范围
            if rgb_array.dtype == np.uint8:
                r = r / 255.0
                g = g / 255.0
                b = b / 255.0
        
        # 计算总和
        total = r + g + b
        
        # 避免除零，找出总和不为0的像素（即非纯黑色素）
        valid_mask = total > 0
        
        # 初始化结果数组
        r_chrom = np.zeros_like(r)
        g_chrom = np.zeros_like(g)
        
        # 计算色度坐标
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r_chrom[valid_mask] = r[valid_mask] / total[valid_mask]
            g_chrom[valid_mask] = g[valid_mask] / total[valid_mask]
        
        return r_chrom.flatten(), g_chrom.flatten(), valid_mask.flatten()
    
    @staticmethod
    def get_file_info(image_path):
        """
        获取图片文件信息
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            dict: 包含文件名、大小、尺寸等信息
        """
        # 获取文件名
        filename = os.path.basename(image_path)
        
        # 获取文件大小
        file_size = os.path.getsize(image_path)
        
        # 格式化文件大小
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        # 获取图片尺寸
        image = Image.open(image_path)
        width, height = image.size
        
        return {
            'filename': filename,
            'file_size': size_str,
            'width': width,
            'height': height
        }
    
    @staticmethod
    def process_image(image_path, color_space='rg_bg', sample_rate=10):
        """
        处理图像：加载、降采样并转换颜色空间
        
        Args:
            image_path: 图像文件路径
            color_space: 颜色空间类型 ('rg_bg' 或 'chromaticity')
            sample_rate: 降采样率
            
        Returns:
            dict: 包含原图、处理后的坐标数据等信息
        """
        # 加载图像
        image = ImageProcessor.load_image(image_path)
        
        # 获取文件信息
        file_info = ImageProcessor.get_file_info(image_path)
        
        # 降采样
        sampled_array = ImageProcessor.downsample_image(image, sample_rate)
        
        # 根据选择的颜色空间进行转换
        if color_space == 'rg_bg':
            x_data, y_data, valid_mask = ImageProcessor.convert_to_normalized_rg(sampled_array)
            x_label = 'r/g'
            y_label = 'b/g'
        else:  # chromaticity
            x_data, y_data, valid_mask = ImageProcessor.convert_to_chromaticity(sampled_array)
            x_label = 'r/(r+g+b)'
            y_label = 'g/(r+g+b)'
        
        # 只保留有效数据点
        x_data = x_data[valid_mask]
        y_data = y_data[valid_mask]
        
        return {
            'original_image': image,
            'x_data': x_data,
            'y_data': y_data,
            'x_label': x_label,
            'y_label': y_label,
            'point_count': len(x_data),
            'file_info': file_info
        }
