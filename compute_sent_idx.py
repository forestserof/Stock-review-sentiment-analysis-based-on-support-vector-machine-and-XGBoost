import os
import pandas as pd
import numpy as np

# 输入和输出文件夹路径
input_folder = './analyzed'
output_folder = './All_merged_new'

# 如果输出文件夹不存在，则创建该文件夹
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 读取上证指数数据
quotes = pd.read_csv('./data/sh000001.csv', parse_dates=['date'])
quotes.set_index('date', inplace=True)

# 定义 BI_Simple_func 和 BI_func 函数
def BI_Simple_func(row):
    pos = row[row == 1].count()
    neg = row[row == 0].count()
    return (pos - neg) / (pos + neg)

def BI_func(row):
    pos = row[row == 1].count()
    neg = row[row == 0].count()
    bi = np.log(1.0 * (1 + pos) / (1 + neg))
    return bi

# 遍历 analyzed 文件夹中的所有 CSV 文件
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        # 读取 CSV 文件
        file_path = os.path.join(input_folder, file_name)
        df = pd.read_csv(file_path, parse_dates=['created_time'])

        # 按日期分组，计算 BI 和 BI_Simple 指标
        grouped = df['polarity'].groupby(df.created_time.dt.date)
        BI_Simple_index = grouped.apply(BI_Simple_func)
        BI_index = grouped.apply(BI_func)

        # 合并 BI 和 BI_Simple 指标
        sentiment_idx = pd.concat([BI_index.rename('BI'), BI_Simple_index.rename('BI_Simple')], axis=1)

        # 将 sentiment_idx 和 quotes 合并，填充缺失值
        sentiment_idx.index = pd.to_datetime(sentiment_idx.index)
        merged = pd.merge(sentiment_idx, quotes, how='left', left_index=True, right_index=True)
        merged.fillna(method='ffill', inplace=True)

        # 计算 BI 和 BI_Simple 的移动平均值
        merged['BI_MA'] = merged['BI'].rolling(window=2, center=False).mean()
        merged['BI_Simple_MA'] = merged['BI_Simple'].rolling(window=2, center=False).mean()

        # 保存处理后的文件到 All_merged 文件夹
        output_file_path = os.path.join(output_folder, f'all_{file_name}')
        merged.to_csv(output_file_path)
        print(f'Processed and saved: {output_file_path}')

print("All files have been processed and saved to the 'All_merged' folder.")
