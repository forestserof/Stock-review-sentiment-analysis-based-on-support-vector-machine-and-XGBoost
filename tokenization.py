import os
import pandas as pd
import jieba
import re  # 导入正则表达式模块

# 设置文件夹路径
folder_path = 'Industry_Data'

# 获取文件夹中的所有 CSV 文件
csv_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.csv')]

# 定义一个函数用于去除标点符号
def remove_punctuation(text):
    # 使用正则表达式替换所有非字母、数字和中文字符为 ''
    return re.sub(r'[^\w\s\u4e00-\u9fa5]', '', text)

# 对每个 CSV 文件进行处理
for csv_file in csv_files:
    # 读取 CSV 文件
    df = pd.read_csv(csv_file)

    # 检查 CSV 文件的列名，确保是 'title' 和 'created_time'
    if 'title' not in df.columns or 'created_time' not in df.columns:
        print(f"文件 {csv_file} 的列名不符合要求，跳过此文件。")
        continue

    # 对 'title' 列进行分词处理，并去除标点符号
    df['title'] = df['title'].apply(lambda x: " ".join(jieba.cut(str(x))) if pd.notnull(x) else "").apply(remove_punctuation)

    # 保存处理后的结果到新的 CSV 文件
    output_file = csv_file.replace('.csv', '_processed.csv')
    df.to_csv(output_file, index=False)

    print(f"文件 {csv_file} 处理完成，结果已保存为 {output_file}")
