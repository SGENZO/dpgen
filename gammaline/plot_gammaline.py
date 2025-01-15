import matplotlib.pyplot as plt

# 读取数据
with open('gammaline/result') as f:
    lines = f.readlines()

# 解析数据
x = []
y1 = []  # 110_110
y2 = []  # 110_111
for line in lines[1:]:  # 跳过第一行标题
    parts = line.strip().split()
    x.append(int(parts[0]))
    y1.append(float(parts[1]))
    y2.append(float(parts[3]))

# 绘制曲线
plt.figure(figsize=(10, 6))
plt.plot(x, y1, label='110_110')
plt.plot(x, y2, label='110_111')

# 添加标签和标题
plt.xlabel('Index')
plt.ylabel('Gamma Value')
plt.title('Gammaline Curves')
plt.legend()
plt.grid(True)

# 保存图像
plt.savefig('gammaline/gammaline_plot.png')
plt.show()
