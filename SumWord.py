import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import os
import random
import seaborn as sns
import matplotlib
# 设置matplotlib字体为支持中文的字体
matplotlib.rcParams['font.sans-serif'] = ['Heiti TC']  # 设置字体为 Heiti TC
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

# 确保图片保存目录存在
if not os.path.exists('WordFrequency'):
    os.makedirs('WordFrequency')

# 读取词典文件，创建情感词典
def read_sentiment_dict(filename):
    sentiment_dict = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            words, sentiment = line.strip().split()
            sentiment = int(sentiment)
            for word in words.split():
                sentiment_dict[word] = sentiment
    return sentiment_dict

# 统计情感词汇频次
def count_sentiment_words(data, sentiment_dict):
    positive_count = Counter()
    negative_count = Counter()
    for title in data['title']:
        # 确保标题是字符串类型
        if isinstance(title, str):
            words = title.split()
            for word in words:
                if word in sentiment_dict:
                    if sentiment_dict[word] == 1:
                        positive_count[word] += 1
                    elif sentiment_dict[word] == -1:
                        negative_count[word] += 1
    return positive_count, negative_count

# 绘制柱状图并保存
def plot_bar_chart(word_counts, title, sentiment, industry):
    words, freqs = zip(*word_counts.most_common(10))
    num_colors = len(words)

    # 创建DataFrame用于Seaborn绘图
    df = pd.DataFrame({
        '词汇': words,
        '频率': freqs
    })

    plt.figure(figsize=(12, 6))  # 调整图形大小

    # 使用Seaborn绘制柱状图
    sns.barplot(x='词汇', y='频率', data=df, palette=sns.color_palette("hsv", num_colors), edgecolor='black', linewidth=1)

    plt.xlabel('词汇', fontsize=14)
    plt.ylabel('频率', fontsize=14)
    plt.title(f'{industry}行业{title}中前10个{sentiment}词汇', fontsize=16)
    plt.xticks(rotation=45, ha="right", fontsize=12)  # 旋转x轴标签，避免重叠
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # 添加y轴网格线
    plt.tight_layout()  # 自动调整子图参数, 使之填充整个图像区域

    # 在柱子上方添加数据标签
    for i, freq in enumerate(freqs):
        plt.text(i, freq + 0.05, str(freq), ha='center', va='bottom', fontsize=10)

    # 保存图表
    plt.savefig(f'./WordFrequency/{industry}_{title}_{sentiment}.png')
    plt.show()

# 处理所有文件
def process_files():
    # 读取情感词典
    sentiment_dict = read_sentiment_dict('./data/Jiang20Yao21_media_sentiment_score.txt')

    # 文件列表和对应的行业
    files = [
        ('merged_industrial_data_processed.csv', '工业'),
        ('merged_consumer_data_processed.csv', '消费者'),
        ('merged_energy_data_processed.csv', '能源'),
        ('merged_finance_data_processed.csv', '金融'),
        ('merged_healthcare_data_processed.csv', '医疗'),
        ('merged_technology_data_processed.csv', '科技'),
        ('merged_shanghai_index_data_processed.csv', '上证指数')
    ]

    for filename, industry in files:
        # 读取数据文件
        data = pd.read_csv(f'./data/{filename}')

        # 统计情感词汇频次
        positive_count, negative_count = count_sentiment_words(data, sentiment_dict)

        # 绘制柱状图并保存
        plot_bar_chart(positive_count, '股评', '积极', industry)
        plot_bar_chart(negative_count, '股评', '消极', industry)

process_files()
