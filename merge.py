import os
import pandas as pd

# 设置文件夹路径
folder_path = '科技行业'

# 获取文件夹中的所有 CSV 文件
csv_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]

# 初始化一个空的 DataFrame 用于存储合并后的数据
combined_df = pd.DataFrame()

# 遍历每个 CSV 文件并进行合并
for csv_file in csv_files:
    # 读取 CSV 文件
    df = pd.read_csv(csv_file)

    # 检查列名是否符合要求
    if 'title' in df.columns and 'created_time' in df.columns:
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    else:
        print(f"文件 {csv_file} 不符合要求，跳过此文件。")

# 保存合并后的数据到新的 CSV 文件
output_file = 'merged_technology_data.csv'
combined_df.to_csv(output_file, index=False)

print(f"所有文件已合并，结果已保存为 {output_file}")
