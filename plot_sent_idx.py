import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# 确保 matplotlib 支持中文显示
matplotlib.rcParams['font.sans-serif'] = ['Heiti TC']  # 设置字体为 Heiti TC
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
sns.set(style="white")

# 输入文件夹路径
input_folder = './All_merged'
output_folder = './visualization_idx_sentiment'

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 遍历 All_merged 文件夹中的每个 CSV 文件
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        # 提取文件名的一部分（如 consumer_data）
        title_part = '_'.join(file_name.split('_')[2:4])

        # 读取 CSV 文件
        file_path = os.path.join(input_folder, file_name)
        df = pd.read_csv(file_path, parse_dates=['created_time'])

        # 将 close 列中的字符串数值（包含逗号）转换为数值
        df['close'] = df['close'].replace({',': ''}, regex=True).astype(float)

        # 设置索引为日期
        df.set_index('created_time', inplace=True)

        # 过滤数据，只选择 2024-07-01 到 2024-09-30 期间的数据
        df_filtered = df.loc['2024-07-01':'2024-09-30']

        # 创建图表
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # 绘制 close 值的变化趋势（左侧 y 轴）使用 seaborn 绘图
        sns.lineplot(x=df_filtered.index, y=df_filtered['close'], ax=ax1, color='b', label='Close', linestyle='-')
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('close', fontsize=12, color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        # 创建第二个 y 轴（右侧 y 轴）
        ax2 = ax1.twinx()
        sns.lineplot(x=df_filtered.index, y=df_filtered['BI'], ax=ax2, color='g', label='BI', linestyle='--')
        ax2.set_ylabel('BI', fontsize=12, color='g')
        ax2.tick_params(axis='y', labelcolor='g')

        # 设置图表标题
        plt.title(f"{title_part} 2024年7月1日到9月30日 Close 值与 BI 变化趋势", fontsize=14, fontproperties='Heiti TC')

        # 显示图例
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        # 调整布局和标签旋转
        plt.xticks(rotation=45)
        plt.tight_layout()

        # 保存图表到指定文件夹
        output_path = os.path.join(output_folder, f"{title_part}_trend.png")
        plt.savefig(output_path)
        plt.close()

        print(f"图表已保存到: {output_path}")
