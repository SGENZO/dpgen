import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# 读取数据
with open('enthalpy/result', 'r') as f:
    lines = f.readlines()

# 解析 FCC vs HCP 数据
fcc_hcp_data = []
for line in lines[2:9]:
    parts = line.split()
    pressure = float(parts[0])
    hcp = float(parts[3])
    fcc = float(parts[1])
    fcc_hcp_data.append((pressure, hcp - fcc))

# 解析 HCP_high vs BCC 数据
hcp_bcc_data = []
for line in lines[13:]:
    if not line.strip():
        continue
    parts = line.split()
    pressure = float(parts[0])
    bcc = float(parts[3])
    hcp_high = float(parts[1])
    hcp_bcc_data.append((pressure, bcc - hcp_high))

# 处理 DFT 数据
dft_data = [
    (0.0, 0.0129),
    (50.0, 0.0123),
    (100.0, 0.0052),
    (150.0, 0.0002),
    (200.0, -0.0043),
    (250.0, -0.0086),
    (300.0, -0.0125)
]

# 处理 DP-PbSn-old 数据
dp_data = [
    (0.0, 0.0099),
    (50.0, 0.0049),
    (100.0, 0.0009),
    (150.0, -0.0021),
    (200.0, -0.0060),
    (250.0, -0.0101),
    (300.0, -0.0131)
]

hcp_bcc_dft_data = [
    (850.0, -1524.1955+1531.1505),
    (900.0, -1523.6292+1531.1505),
    (950.0, -1523.0725+1531.1505),
    (1000.0, -1522.5053+1531.1505),
]


# 绘制 HCP-FCC 曲线
plt.figure(figsize=(10, 6))

# HCP-FCC 光滑曲线
pressures = np.asarray([x[0]/1000 for x in fcc_hcp_data])
deltas = np.asarray([x[1] for x in fcc_hcp_data])
x_new = np.linspace(pressures.min(), pressures.max(), 300)
spl = make_interp_spline(pressures, deltas, k=3)
y_smooth = spl(x_new)
plt.plot(x_new, y_smooth, 'b-', label='DP-PbSn')
plt.scatter(pressures, deltas, color='blue')

# DFT 光滑曲线
dft_pressures = np.asarray([x[0] for x in dft_data])
dft_deltas = np.asarray([x[1] for x in dft_data])
x_new_dft = np.linspace(dft_pressures.min(), dft_pressures.max(), 300)
spl_dft = make_interp_spline(dft_pressures, dft_deltas, k=3)
y_smooth_dft = spl_dft(x_new_dft)
plt.plot(x_new_dft, y_smooth_dft, 'r-', label='DFT')
plt.scatter(dft_pressures, dft_deltas, color='red')

# DP-PbSn-old 光滑曲线
dp_pressures = np.asarray([x[0]for x in dp_data])
dp_deltas = np.asarray([x[1] for x in dp_data])
x_new_dp = np.linspace(dp_pressures.min(), dp_pressures.max(), 300)
spl_dp = make_interp_spline(dp_pressures, dp_deltas, k=3)
y_smooth_dp = spl_dp(x_new_dp)
plt.plot(x_new_dp, y_smooth_dp, 'g-', label='DP-PbSn-old')
plt.scatter(dp_pressures, dp_deltas, color='green')

plt.xlabel('Pressure (Kbar)')
plt.ylabel('Enthalpy Difference (eV)')
plt.title('HCP - FCC Enthalpy Prediction')
plt.grid(True)
plt.legend()
plt.savefig('enthalpy/hcp_fcc.png')


# DFT 光滑曲线
dft_pressures = np.asarray([x[0] for x in hcp_bcc_dft_data])
dft_deltas = np.asarray([x[1] for x in hcp_bcc_dft_data])
x_new_dft = np.linspace(dft_pressures.min(), dft_pressures.max(), 300)
spl_dft = make_interp_spline(dft_pressures, dft_deltas, k=3)
y_smooth_dft = spl_dft(x_new_dft)
plt.plot(x_new_dft, y_smooth_dft, 'r-', label='DFT')
plt.scatter(dft_pressures, dft_deltas, color='red')

# 绘制 BCC-HCP_high 曲线
plt.figure(figsize=(10, 6))
pressures = np.asarray([x[0]/1000 for x in hcp_bcc_data])
deltas = np.asarray([x[1] for x in hcp_bcc_data])
x_new = np.linspace(pressures.min(), pressures.max(), 300)
spl = make_interp_spline(pressures, deltas, k=3)
y_smooth = spl(x_new)
plt.plot(x_new, y_smooth, 'b-', label='DP-PbSn')
plt.scatter(pressures, deltas, color='blue')
plt.plot(x_new_dft, y_smooth_dft, 'r-', label='DFT')
plt.scatter(dft_pressures, dft_deltas, color='red')
plt.xlabel('Pressure (Kbar)')
plt.ylabel('Enthalpy Difference (eV)')
plt.title('BCC - HCP_high Enthalpy Prediction')
plt.grid(True)
plt.savefig('enthalpy/bcc_hcp_high.png')
