import os
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib

# 设置matplotlib字体为支持中文的字体
matplotlib.rcParams['font.sans-serif'] = ['Heiti TC']  # 设置字体为 Heiti TC
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

# 加载数据文件
file_path = './data/merged_shanghai_index_data_processed.csv'
data = pd.read_csv(file_path)

# 检查列名
print("文件中的列名：", data.columns.tolist())

# 提取文本列（替换为实际包含文本的列名）
text_column = 'title'  # 替换为文件中包含文本的列
if text_column in data.columns:
    text_data = ' '.join(data[text_column].astype(str).dropna().tolist())
else:
    raise ValueError(f"列 '{text_column}' 不存在，请检查数据结构！")

# 加载停用词表
stopwords_path = 'data/all_stopwords.txt'
with open(stopwords_path, 'r', encoding='utf-8') as f:
    stopwords = set([line.strip() for line in f])

# 去停用词
filtered_words = [word for word in text_data.split() if word not in stopwords]
filtered_text = ' '.join(filtered_words)

# 指定支持中文的字体路径（根据操作系统选择）
# font_path = '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'  # Linux 示例
# font_path = 'C:/Windows/Fonts/simhei.ttf'  # Windows 示例
font_path = '/System/Library/Fonts/STHeiti Light.ttc'  # Mac 示例

# 生成词云图
wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(filtered_text)

# 创建保存文件夹
output_dir = './WordCloud'
os.makedirs(output_dir, exist_ok=True)  # 如果文件夹不存在，自动创建

# 保存词云图到文件
output_path = os.path.join(output_dir, 'shanghai_index_wordcloud.png')
wordcloud.to_file(output_path)

# 显示词云
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('上证指数股评词云图', fontsize=16)
plt.show()

print(f"词云图已保存到: {output_path}")
