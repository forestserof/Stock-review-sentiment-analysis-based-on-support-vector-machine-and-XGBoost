import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Heiti TC']  # 设置字体为 Heiti TC
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
# 文件路径
data_path = './All_merged/all_merged_shanghai_index_data_processed_analyzed.csv'

# 加载数据
df = pd.read_csv(data_path)
df['volume'] = df['volume'].str.replace('B', '').astype(float) * 1e9
# 检查数据的基本信息
print("原始数据前五行:")
print(df.head())
print("\n原始数据的信息:")
print(df.info())

# 处理时间列，并将其设置为索引
df['created_time'] = pd.to_datetime(df['created_time'], format='%Y/%m/%d %H:%M', errors='coerce')

# 删除无法解析的时间数据
df.dropna(subset=['created_time'], inplace=True)
df.set_index('created_time', inplace=True)

# 检查数据的时间范围
print(f"数据时间范围: {df.index.min()} 到 {df.index.max()}")

# 筛选 7 到 9 月的数据
df = df[(df.index.month >= 7) & (df.index.month <= 9)]
if df.empty:
    raise ValueError("筛选 7 到 9 月的数据后为空，请检查原始数据的时间范围！")

# 数据清理：去除包含逗号的数字列，并转换为浮点型
cols_to_clean = ['open', 'high', 'low', 'close', 'volume']
for col in cols_to_clean:
    df[col] = df[col].replace({',': ''}, regex=True)  # 去除逗号
    df[col] = pd.to_numeric(df[col], errors='coerce')  # 转换为浮点型

# 填充缺失值
df.fillna(method='ffill', inplace=True)
df.fillna(method='bfill', inplace=True)
if df.empty:
    raise ValueError("数据清理后为空，请检查清理步骤！")

# 检查必要的列
required_cols = ['open', 'high', 'low', 'close', 'volume', 'BI_Simple']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"缺失必要的列: {missing_cols}")

# 设置滞后特征
lag_days = 2  # 滞后天数
for lag in range(1, lag_days + 1):
    for col in ['open', 'high', 'low', 'volume', 'BI_Simple']:
        df[f'{col}_lag{lag}'] = df[col].shift(lag)

# 删除因滞后特征引入的缺失值
df.dropna(inplace=True)

# 保存处理后的数据
output_path = './lagged_data.csv'
df.to_csv(output_path)
print(f"滞后特征数据已保存到: {output_path}")

# 选择特征列 X 和目标变量 y
lagged_cols = ['open', 'high', 'low', 'volume', 'BI_Simple'] + [f'{col}_lag{lag}' for lag in range(1, lag_days + 1) for col in ['open', 'high', 'low', 'volume', 'BI_Simple']]
X = df[lagged_cols]
y = df['close']

# 特征标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 拆分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# 创建 XGBoost 回归模型
model = XGBRegressor(objective='reg:squarederror', random_state=42)

# 设置超参数搜索空间
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 6, 10],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.7, 0.8, 1.0],
    'colsample_bytree': [0.7, 0.8, 1.0]
}

# 使用 GridSearchCV 进行超参数调优
grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=3, scoring='neg_mean_squared_error', verbose=1)
grid_search.fit(X_train, y_train)

# 输出最佳参数
print(f"最佳参数: {grid_search.best_params_}")

# 使用最佳参数的模型进行预测
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

# 模型评估
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'MSE: {mse}')
print(f'RMSE: {rmse}')
print(f'MAE: {mae}')
print(f'R²: {r2}')

# 可视化预测结果
plt.figure(figsize=(10, 6))
plt.scatter(range(len(y_test)), y_test, color='blue', label='真实值', alpha=0.6)
plt.scatter(range(len(y_pred)), y_pred, color='red', label='预测值', alpha=0.6)
plt.title("真实值与预测值的对比（7月至9月）")
plt.xlabel("样本索引")
plt.ylabel("收盘价")
plt.legend()
plt.grid(linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

"""R² 是一个衡量模型拟合优度的指标，表示模型能解释目标变量方差的比例。R² 值的范围是 0 到 1，越接近 1 表示模型对数据的拟合程度越好。R² = 0.9906 表明模型能够解释约 99.06% 的数据方差，这意味着模型的预测能力非常强，几乎能够完美拟合数据。"""