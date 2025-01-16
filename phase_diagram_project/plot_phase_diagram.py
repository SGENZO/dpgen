import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.interpolate import UnivariateSpline

# 读取数据
data_dir = 'phase_diagram_project/data'  # 修正数据路径
phases = {
    'fcc': {'file': 'fcc.csv', 'color': '#1f77b4', 'linestyle': '-', 'linewidth': 5},
    'hcp': {'file': 'hcp.csv', 'color': '#ff7f0e', 'linestyle': '--', 'linewidth': 5}, 
    'bcc': {'file': 'bcc.csv', 'color': '#2ca02c', 'linestyle': '-.', 'linewidth': 5},
    'reference': {'file': 'melt_curve.csv', 'color': '#d62728', 'linestyle': ':', 'linewidth': 5}
}

plt.figure(figsize=(12, 8))

# 绘制每个相的数据
for phase, config in phases.items():
    filepath = os.path.join(data_dir, config['file'])
    data = pd.read_csv(filepath)
    
    # 使用1000K单位
    pressure = data['pressure_GPa']
    temperature = data['temperature_1000K']
    
    # 对所有曲线进行平滑处理
    spline = UnivariateSpline(pressure, temperature, s=0.5)
    pressure_smooth = np.linspace(pressure.min(), pressure.max(), 200)
    temperature_smooth = spline(pressure_smooth)
    
    # 绘制平滑后的曲线
    plt.plot(pressure_smooth, temperature_smooth,
             color=config['color'],
             linestyle=config['linestyle'],
             linewidth=config['linewidth'],
             label=phase.upper())

# 添加标签和标题
plt.xlabel('Pressure (GPa)', fontsize=14)
plt.ylabel('Temperature (1000K)', fontsize=14)
plt.title('Phase Diagram', fontsize=16)

# 设置坐标轴范围
plt.xlim(0, 100)
plt.ylim(bottom=0)

# 获取reference曲线数据
ref_data = phases['reference']
ref_filepath = os.path.join(data_dir, ref_data['file'])
ref_df = pd.read_csv(ref_filepath)
ref_spline = UnivariateSpline(ref_df['pressure_GPa'], ref_df['temperature_1000K'], s=0.5)

# 在x=15.12处画垂直线
x1 = 15.12
y1 = ref_spline(x1)
plt.plot([x1, x1], [0, y1], color='gray', linestyle='--', linewidth=1)

# 在x=40.85处画点并与(101.46,0)连线
x2 = 40.85
y2 = ref_spline(x2)
x3 = 101.46
y3 = 0
plt.plot([x2, x3], [y2, y3], color='gray', linestyle='--', linewidth=1)

# 生成reference曲线的x,y点
x_ref = np.linspace(0, x3, 200)
y_ref = ref_spline(x_ref)

# 添加区域背景色
# FCC区域
fcc_x = np.linspace(0, x1, 100)
fcc_y = ref_spline(fcc_x)
plt.fill_between(fcc_x, 0, fcc_y, color='lightgray', alpha=0.3)

# HCP区域
hcp_x1 = np.linspace(x1, x2, 100)
hcp_y1 = ref_spline(hcp_x1)
hcp_x2 = np.linspace(x2, x3, 100)
hcp_y2 = np.linspace(y2, y3, 100)
hcp_x = np.concatenate([hcp_x1, hcp_x2])
hcp_y = np.concatenate([hcp_y1, hcp_y2])
plt.fill_between(hcp_x, 0, hcp_y, color='lightcoral', alpha=0.3)

# BCC区域
bcc_x = np.linspace(x2, x3, 100)
bcc_y = ref_spline(bcc_x)
line_y = np.linspace(y2, y3, 100)
plt.fill_between(bcc_x, line_y, bcc_y, color='lightblue', alpha=0.3)

# 添加区域标注
plt.text((x1)/2, (0+y1)/4, 'FCC', fontsize=24, ha='center', va='center')
plt.text((x1 + x2)/1.3, (y1 + y2)/4, 'HCP', fontsize=24, ha='center', va='center') 
plt.text((x2 + x3)/2, y2, 'BCC', fontsize=24, ha='center', va='center')

# 获取hcp曲线数据
hcp_data = phases['hcp']
hcp_filepath = os.path.join(data_dir, hcp_data['file'])
hcp_df = pd.read_csv(hcp_filepath)
hcp_spline = UnivariateSpline(hcp_df['pressure_GPa'], hcp_df['temperature_1000K'], s=0.5)

# 计算并标注x=2和x=45处的点
x_points = [2.5, 35]
for x in x_points:
    y = hcp_spline(x)
    plt.plot(x, y, 'ro', markersize=8)
    plt.annotate(f'({x:.1f}, {y:.2f})', 
                 xy=(x, y), 
                 xytext=(x, y+0.5),
                 fontsize=12,
                 arrowprops=dict(facecolor='black', shrink=0.05))

# 设置网格和图例
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12, loc='upper left')

# 调整布局
plt.tight_layout()

# 保存图像
plt.savefig('phase_diagram_project/phase_diagram.png', dpi=300, bbox_inches='tight')

# 显示图像
plt.show()
