#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DeepMD 测试误差热力学区域热图绘制脚本
用于分析test_error.log文件中的测试误差，并在压力-温度二维平面上绘制热图
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import matplotlib as mpl
import platform

def setup_chinese_font():
    """
    设置中文字体
    """
    system = platform.system()
    if system == "Darwin":  # macOS
        plt.rcParams["font.family"] = ["Arial Unicode MS"]
    elif system == "Windows":  # Windows
        plt.rcParams["font.family"] = ["Microsoft YaHei"]
    elif system == "Linux":  # Linux
        plt.rcParams["font.family"] = ["DejaVu Sans"]
    
    # 设置正常显示负号
    mpl.rcParams['axes.unicode_minus'] = False

def parse_test_error_log(file_path):
    """
    解析test_error.log文件，提取系统信息和误差数据
    
    Args:
        file_path (str): test_error.log文件的路径
    
    Returns:
        pd.DataFrame: 包含解析后数据的DataFrame
    """
    data = []
    current_system = None
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        # 匹配系统信息
        system_match = re.search(r'testing system : (?:.*/)?([^/]+)/([^/]+)/([^/]+)/deepmd', line)
        if system_match:
            composition = system_match.group(1)
            phase = system_match.group(2)
            condition = system_match.group(3)
            
            # 提取组分（去除相信息）
            composition = re.sub(r'^(fcc|bcc|hcp)', '', composition)
            
            # 解析压力和温度
            pressure_temp = re.match(r'(\d+)G_(\d+)K', condition)
            if pressure_temp:
                pressure = int(pressure_temp.group(1))
                temperature = int(pressure_temp.group(2)) / 1000
                current_system = {
                    'composition': composition,
                    'phase': phase,
                    'pressure': pressure,
                    'temperature': temperature
                }
        
        # 匹配误差数据
        if current_system:
            energy_rmse = re.search(r'Energy RMSE/Natoms\s+: ([\d.e-]+)', line)
            force_rmse = re.search(r'Force  RMSE\s+: ([\d.e-]+)', line)
            virial_rmse = re.search(r'Virial RMSE/Natoms\s+: ([\d.e-]+)', line)
            
            if energy_rmse:
                current_system['energy_rmse'] = float(energy_rmse.group(1))
            if force_rmse:
                current_system['force_rmse'] = float(force_rmse.group(1))
            if virial_rmse:
                current_system['virial_rmse'] = float(virial_rmse.group(1))
                data.append(current_system.copy())
                current_system = None
    
    return pd.DataFrame(data)

def get_error_ranges(df, error_types):
    """
    获取每种误差类型的最大最小值
    
    Args:
        df (pd.DataFrame): 包含所有数据的DataFrame
        error_types (list): 误差类型列表
    
    Returns:
        dict: 包含每种误差类型的最大最小值
    """
    ranges = {}
    for error_type in error_types:
        ranges[error_type] = {
            'vmin': df[error_type].min(),
            'vmax': df[error_type].max()
        }
    return ranges

def format_value(val):
    """
    格式化数值，处理NaN值
    """
    if pd.isna(val):
        return ''
    return f'{val:.2e}'

def plot_heatmap_phases(df, composition, error_type, error_name, save_dir, error_ranges):
    """
    为指定组分的所有相绘制热图
    
    Args:
        df (pd.DataFrame): 包含所有数据的DataFrame
        composition (str): 要绘制的组分
        error_type (str): 误差类型（列名）
        error_name (str): 误差类型的中文名称
        save_dir (str): 保存图片的目录
        error_ranges (dict): 每种误差类型的取值范围
    """
    # 筛选特定组分的数据
    comp_data = df[df['composition'] == composition].copy()
    
    # 获取该组分的所有相
    phases = sorted(comp_data['phase'].unique())
    
    # 创建子图
    fig, axes = plt.subplots(1, len(phases), figsize=(6*len(phases), 5))
    if len(phases) == 1:
        axes = [axes]
    
    # 获取该误差类型的最大最小值
    vmin = error_ranges[error_type]['vmin']
    vmax = error_ranges[error_type]['vmax']
    
    # 为每个相绘制热图
    for ax, phase in zip(axes, phases):
        # 筛选特定相的数据
        phase_data = comp_data[comp_data['phase'] == phase].copy()
        
        # 创建压力-温度网格
        pivot_table = phase_data.pivot(index='temperature', columns='pressure', values=error_type)
        
        # 创建注释数组
        #annot = pivot_table.applymap(format_value)
        
        # 绘制热图
        sns.heatmap(pivot_table, 
                    #annot=annot,
                    fmt='',  # 使用空字符串，因为我们已经格式化了数值
                    cmap='viridis',
                    xticklabels=True, 
                    yticklabels=True, 
                    ax=ax,
                    vmin=vmin, 
                    vmax=vmax,
                    mask=pivot_table.isna(),
                    cbar=False,
                    #annot_kws={'color': 'black'},  # 添加这行：将注释文字改为黑色
                    )
        # 反转y轴（压力轴）
        ax.invert_yaxis()
        
        #ax.set_title(f'{phase}相')
        ax.set_xlabel('压力 (GPa)') 
        ax.set_ylabel('温度 (1000K)')
    
    # 添加总标题
    fig.suptitle(f'{composition} - {error_name}', fontsize=14)
    
    # 添加统一的颜色条
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  # [left, bottom, width, height]
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap='viridis'),
                cax=cbar_ax, label=error_name)
    
    # 调整子图之间的间距
    plt.subplots_adjust(top=0.85, right=0.9, wspace=0.3)
    
    # 保存图片
    save_path = os.path.join(save_dir, f'{composition}_{error_type}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_combined_heatmap(df, error_types, error_names, error_ranges, save_dir):
    """
    将所有组分和统计量绘制在一张大图上
    
    Args:
        df (pd.DataFrame): 包含所有数据的DataFrame
        error_types (list): 误差类型列表
        error_names (list): 误差类型名称列表
        error_ranges (dict): 每种误差类型的取值范围
        save_dir (str): 保存图片的目录
    """
    # 获取所有唯一的组分
    compositions = sorted(df['composition'].unique())
    n_compositions = len(compositions)
    n_error_types = len(error_types)
    
    # 创建大图
    fig = plt.figure(figsize=(6*n_error_types, 5*n_compositions))
    gs = fig.add_gridspec(n_compositions, n_error_types, hspace=0.4, wspace=0.3)
    
    # 为每个组分和误差类型创建子图
    for i, composition in enumerate(compositions):
        for j, (error_type, error_name) in enumerate(zip(error_types, error_names)):
            # 创建子图
            ax = fig.add_subplot(gs[i, j])
            
            # 获取该组分的数据
            comp_data = df[df['composition'] == composition].copy()
            phases = sorted(comp_data['phase'].unique())
            
            # 计算每个相的子图宽度
            phase_width = 1.0 / len(phases)
            
            # 获取该误差类型的最大最小值
            vmin = error_ranges[error_type]['vmin']
            vmax = error_ranges[error_type]['vmax']
            
            # 为每个相创建子图
            for k, phase in enumerate(phases):
                # 计算子图位置
                pos = k * phase_width
                
                # 创建相的子图区域
                phase_ax = ax.inset_axes([pos, 0, phase_width, 1.0])
                
                # 筛选相数据
                phase_data = comp_data[comp_data['phase'] == phase].copy()
                pivot_table = phase_data.pivot(index='temperature', columns='pressure',
                                             values=error_type)
                
                # 绘制热图
                sns.heatmap(pivot_table, 
                           cmap='viridis',
                           xticklabels=True if k == len(phases)-1 else False,
                           yticklabels=True if k == 0 else False,
                           ax=phase_ax,
                           vmin=vmin, 
                           vmax=vmax,
                           mask=pivot_table.isna(),
                           cbar=False)
                
                # 反转y轴
                phase_ax.invert_yaxis()
                
                # 设置标题
                if i == 0:
                    phase_ax.set_title(f'{phase}相' if k == 1 else '')
                
                # 设置标签
                if k == 0:
                    phase_ax.set_ylabel('温度 (1000K)')
                if k == len(phases)-1:
                    phase_ax.set_xlabel('压力 (GPa)')
            
            # 设置行标题（组分）和列标题（误差类型）
            if j == 0:
                ax.text(-0.2, 0.5, composition, 
                       rotation=90, va='center', ha='right',
                       transform=ax.transAxes, fontsize=12)
            if i == 0:
                ax.text(0.5, 1.2, error_name,
                       ha='center', va='bottom',
                       transform=ax.transAxes, fontsize=12)
            
            # 隐藏主坐标轴
            ax.set_axis_off()
    
    # 添加统一的颜色条
    for j, (error_type, error_name) in enumerate(zip(error_types, error_names)):
        cbar_ax = fig.add_axes([0.92, 1.0 - (j+1)/n_error_types + 0.1, 0.02, 0.2])
        norm = mpl.colors.Normalize(vmin=error_ranges[error_type]['vmin'],
                                  vmax=error_ranges[error_type]['vmax'])
        fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap='viridis'),
                    cax=cbar_ax, label=error_name)
    
    # 保存图片
    save_path = os.path.join(save_dir, 'combined_heatmap.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # 设置中文字体
    setup_chinese_font()
    
    # 创建保存图片的目录
    save_dir = 'initmodel01'
    #os.makedirs(save_dir, exist_ok=True)
    
    # 读取数据
    df = parse_test_error_log('initmodel01/test_err.log')
    print("数据概览：")
    print(df.head())
    print("\n发现的不同组分：")
    print(df['composition'].unique())
    
    # 定义误差类型
    error_types = ['energy_rmse', 'force_rmse', 'virial_rmse']
    error_names = ['Energy RMSE/Natoms (eV)', 'Force RMSE (eV/Å)', 'Virial RMSE/Natoms (eV)']
    
    # 获取每种误差类型的取值范围
    error_ranges = get_error_ranges(df, error_types)
    
    # 生成单独的热图
    for composition in df['composition'].unique():
        print(f"\n正在生成 {composition} 的热力学误差分布图...")
        for error_type, error_name in zip(error_types, error_names):
            plot_heatmap_phases(df, composition, error_type, error_name, save_dir, error_ranges)
    
    # 生成综合热图
    print("\n正在生成综合热图...")
    plot_combined_heatmap(df, error_types, error_names, error_ranges, save_dir)
    
    print(f"\n所有热图已保存到 {save_dir} 目录")

if __name__ == "__main__":
    main()
