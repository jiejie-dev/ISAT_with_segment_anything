"""
修改ISAT程序的logo和标题的工具

使用前请确保已安装以下工具：
1. pyrcc5 (PyQt5资源编译器)
   - macOS: brew install pyqt5
   - Ubuntu/Debian: sudo apt-get install pyqt5-dev-tools
   - Windows: pip install pyqt5-tools

2. lrelease (Qt语言工具)
   - macOS: brew install qt
   - Ubuntu/Debian: sudo apt-get install qttools5-dev-tools
   - Windows: 安装Qt SDK或使用pyqt5-tools中的lrelease

使用方法：
1. 修改logo：
   python customize_qt.py --logo /path/to/your/logo.svg

2. 修改窗口标题：
   python customize_qt.py --title "您的标题"

3. 同时修改logo和标题：
   python customize_qt.py --logo /path/to/your/logo.svg --title "您的标题"
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse
import shutil

def get_isat_root():
    """获取ISAT根目录"""
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if (current_dir / "ISAT").exists():
            return current_dir / "ISAT"
        current_dir = current_dir.parent
    raise FileNotFoundError("未找到ISAT目录")

def generate_icons(logo_path: str):
    """
    生成所有需要的图标文件
    
    Args:
        logo_path (str): 原始logo图片的路径
    """
    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo文件不存在: {logo_path}")
        
    icons_dir = Path.cwd() / "icons"
    
    # 生成所有版本的图标
    versions = ["11", "12", "13", "14", "21", "22", "23", "24"]
    for version in versions:
        # 复制到标准版本
        shutil.copy2(logo_path, icons_dir / f"ISAT{version}.svg")
        # 复制到100版本
        shutil.copy2(logo_path, icons_dir / f"ISAT{version}_100.svg")
        
    print(f"已生成所有版本的图标文件")

def update_icons_qrc():
    """
    更新ISAT的图标资源文件
    """
    isat_root = get_isat_root()
    
    # 编译资源文件
    qrc_path = isat_root / "icons.qrc"
    try:
        subprocess.run(["pyrcc5", str(qrc_path), "-o", str(isat_root / "icons_rc.py")], check=True)
        print(f"资源文件已编译")
    except subprocess.CalledProcessError as e:
        print(f"编译资源文件失败: {str(e)}")

def update_translation(window_title: str):
    """
    更新ISAT的翻译文件
    
    Args:
        window_title (str): 窗口标题
    """
    isat_root = get_isat_root()
    ui_dir = isat_root / "ui"
    
    # 更新中文翻译文件
    zh_cn_path = ui_dir / "zh_CN.ts"
    if not zh_cn_path.exists():
        raise FileNotFoundError(f"未找到中文翻译文件: {zh_cn_path}")
        
    # 读取并更新翻译文件
    with open(zh_cn_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 替换窗口标题
    import re
    content = re.sub(
        r'<source>ISAT</source>\s*<translation>.*?</translation>',
        f'<source>ISAT</source>\n        <translation>{window_title}</translation>',
        content
    )
    
    # 写回文件
    with open(zh_cn_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    # 编译翻译文件
    try:
        subprocess.run(["lrelease", str(zh_cn_path), "-qm", str(ui_dir / "zh_CN.qm")], check=True)
        print(f"窗口标题已更新为: {window_title}")
    except subprocess.CalledProcessError as e:
        print(f"编译翻译文件失败: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='修改ISAT程序的logo和标题')
    parser.add_argument('--logo', '-l', help='logo图片的路径')
    parser.add_argument('--title', '-t', help='窗口标题')
    
    args = parser.parse_args()
    
    if not args.logo and not args.title:
        print("请至少指定一个参数：--logo 或 --title")
        return
        
    try:
        if args.logo:
            generate_icons(args.logo)
            update_icons_qrc()
            
        if args.title:
            update_translation(args.title)
            
    except Exception as e:
        print(f"操作失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 