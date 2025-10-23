**English** | [简体中文](./README.md)

# Image Color Space Analyzer

A Python-based image color space analysis tool that provides 2x2 four independent analysis windows, capable of analyzing color distributions of multiple images simultaneously.

## Features

### Two Working Modes

#### 1. Multi-block Mode
- **Four Independent Analysis Blocks**: Process multiple images simultaneously
- **Dual Display**: Each block shows the original image on the left and color space statistics on the right
- **Preset Downsampling Rates**: Support options like 1, 5, 10, 20, 50, 100

#### 2. Comparison Mode
- **Single Chart Multiple Datasets**: Compare multiple images in one large chart
- **Different Color Differentiation**: Each image displayed in different colors
- **Custom Downsampling Rate**: Support any integer value input from 1-1000
- **Legend Display**: Automatically generate legends for easy identification
- **Flexible Management**: Add or remove images individually

### General Features
- **Multiple Color Spaces**:
  - r/g, b/g space: Convert RGB to ratio form
  - Chromaticity space: r/(r+g+b), g/(r+g+b) normalized form
- **Dynamic Axes**: Manually adjustable or auto-fit to data range
- **Chart Export**: Support saving statistics as PNG, PDF, SVG, EPS formats
- **Multi-language Support**: Support switching between Chinese and English interface
- **Image Information Display**: Show details like filename, size, dimensions

## Installation Requirements

### Python Version
- Python 3.8 or higher

### Dependencies Installation

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install Pillow numpy matplotlib
```

Note: `tkinter` is usually installed with Python. If missing, install based on your OS:
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- Fedora: `sudo dnf install python3-tkinter`
- macOS: Usually included in Python installation
- Windows: Usually included in Python installation

## Usage

### Start the Program

```bash
python Easy_Look.py
```

### Operation Flow

#### Multi-block Mode Operation
1. **Upload Images**: Click "Upload Image" button in each block
2. **Select Color Space**: Choose r/g,b/g space or chromaticity space
3. **Set Downsampling Rate**: Select preset value from dropdown menu
4. **Adjust Axes**: Manually input or use "Auto Range"
5. **Save Chart**: Click "Save Chart" button

#### Comparison Mode Operation
1. **Switch Mode**: Menu bar → Mode → Comparison Mode
2. **Set Parameters**:
   - Select color space
   - Input custom downsampling rate (1-1000)
3. **Add Images**:
   - Click "Add Image" button
   - Select image file
   - Repeat to add multiple images
4. **Manage Images**:
   - View image list on the left
   - Use "Remove" button to delete specific images
   - Use "Clear All" to remove all images
5. **Adjust View**: Use axis controls to adjust display range
6. **Save Results**: Click "Save Chart" to export comparison results

#### General Operations
- **Switch Language**: Menu bar → Language → Select Chinese or English
- **Batch Operations** (Multi-block mode only):
  - File → Clear All Blocks
  - View → Refresh All Statistics
  - View → Auto Adjust All Axes

## Project Structure

```
.
├── Easy_Look.py               # Main program entry
├── requirements.txt           # Dependencies list
├── README.md                  # Chinese documentation
├── README_en.md              # English documentation
└── modules/                   # Functional modules directory
    ├── __init__.py           # Package initialization
    ├── image_processor.py    # Image processing core module
    ├── image_block.py        # Single image block UI component
    ├── main_window.py        # Main window management module
    ├── comparison_mode.py    # Comparison mode module
    ├── color_picker.py       # Color picker module
    └── language_manager.py   # Multi-language management module
```

## Module Description

### image_processor.py
- `ImageProcessor`: Core image processing class
  - Image loading and format conversion
  - Downsampling processing
  - RGB to r/g, b/g space conversion
  - RGB to chromaticity space conversion

### image_block.py
- `ImageBlock`: Single analysis block component
  - Image upload and display
  - Parameter controls (color space, downsampling rate)
  - Statistics chart drawing
  - Axis range control

### main_window.py
- `MainWindow`: Main window management
  - 2x2 layout management
  - Menu bar functions
  - Batch operation control
  - Status bar display

### comparison_mode.py
- `ComparisonMode`: Comparison mode functionality
  - Multiple images simultaneous comparison
  - Different color dataset display
  - Legend management

### color_picker.py
- `ColorPicker`: Color picker
  - Interactive color selection
  - RGB value display
  - Color space conversion

### language_manager.py
- `LanguageManager`: Multi-language support
  - Chinese-English interface switching
  - Interface text management
  - Language configuration saving

## Color Space Description

### r/g, b/g Space
- Convert RGB values to ratio form
- X-axis: r/g (ratio of red to green)
- Y-axis: b/g (ratio of blue to green)
- Suitable for analyzing relative color intensity relationships

### Chromaticity Space
- Normalized color representation
- X-axis: r/(r+g+b) (proportion of red in total intensity)
- Y-axis: g/(r+g+b) (proportion of green in total intensity)
- Value range: [0, 1]
- Eliminates brightness effects, retaining only chromaticity information

## Usage Suggestions

1. **Large Image Processing**: Use higher downsampling rates (50-100) to improve performance
2. **Comparative Analysis**: Load similar images in different blocks with same parameters for comparison
3. **Color Space Selection**:
   - Use r/g, b/g space for analyzing color tendencies
   - Use chromaticity space for analyzing color purity
4. **Axis Adjustment**: Use "Auto Range" first, then fine-tune as needed

## FAQ

**Q: Program fails to start, showing tkinter missing?**
A: Please install python3-tk package according to your operating system.

**Q: Program freezes when processing large images?**
A: Increase downsampling rate, suggest using 50 or 100.

**Q: Can't see data points in statistics chart?**
A: Check axis range settings, click "Auto Range" button.

**Q: How to save analysis results?**
A: Click "Save Chart" button below each block to save statistics as PNG, PDF, SVG, or EPS format.


## Author

Max