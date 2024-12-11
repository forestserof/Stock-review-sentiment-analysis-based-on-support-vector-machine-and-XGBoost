import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV

# 文件路径和配置
data_path = './data'
pos_corpus = 'positive.txt'
neg_corpus = 'negative.txt'

# Helper function for dummy tokenizer
def dummy_fun(doc):
    return doc

# 加载数据集
def load_dataset_tokenized():
    pos_file = os.path.join(data_path, pos_corpus)
    neg_file = os.path.join(data_path, neg_corpus)

    pos_sents, neg_sents = [], []

    # 加载正面句子
    with open(pos_file, 'r', encoding='utf-8') as f:
        pos_sents = [line.strip().split() for line in f if line.strip()]

    # 加载负面句子
    with open(neg_file, 'r', encoding='utf-8') as f:
        neg_sents = [line.strip().split() for line in f if line.strip()]

    balance_len = min(len(pos_sents), len(neg_sents))
    texts = pos_sents[:balance_len] + neg_sents[:balance_len]
    labels = [1] * balance_len + [0] * balance_len

    return texts, labels

# 模型训练和评估
def train_and_evaluate_classifier():
    # 加载训练数据
    texts, labels = load_dataset_tokenized()
    vectorizer = TfidfVectorizer(analyzer='word', tokenizer=dummy_fun, preprocessor=dummy_fun, token_pattern=None)

    # 特征提取
    X = vectorizer.fit_transform(texts)
    y = labels

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 定义分类器和参数范围
    clf = LinearSVC(dual=False, max_iter=10000)
    param_grid = {'C': [0.01, 0.1, 1, 10, 100]}  # 调整 C 参数以优化模型

    # 网格搜索以找到最佳参数
    grid_search = GridSearchCV(clf, param_grid, cv=3, scoring='accuracy', verbose=1)
    grid_search.fit(X_train, y_train)

    # 获取最佳模型和参数
    best_clf = grid_search.best_estimator_
    best_params = grid_search.best_params_
    print(f"最佳参数: {best_params}")

    # 评估测试集性能
    y_pred = best_clf.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    print(f"测试集最高准确率: {test_accuracy:.4f}")

    return best_clf, vectorizer, test_accuracy

# 模型评估
def eval_model(comment_file, clf, vectorizer):
    print(f'正在加载数据集: {comment_file}...')
    df = pd.read_csv(comment_file)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['created_time'] = pd.to_datetime(df['created_time'], format='%Y/%m/%d %H:%M')
    df['title'] = df['title'].apply(lambda x: [w.strip() for w in x.split()])

    texts = vectorizer.transform(df['title'])
    preds = clf.predict(texts)
    df['polarity'] = preds

    # 修改输出文件的路径，确保保存在./analyzed目录中
    output_file = os.path.join('./analyzed', os.path.basename(comment_file).replace('.csv', '_analyzed.csv'))

    # 确保目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 保存文件
    df.to_csv(output_file, index=False)
    print(f'处理后的文件已保存: {output_file}')

# 主程序入口
if __name__ == '__main__':
    # 训练并评估分类器
    best_clf, vectorizer, best_accuracy = train_and_evaluate_classifier()

    print(f"分类器已准备好，测试集最高准确率为: {best_accuracy:.4f}")

    # 测试集文件列表
    files = [
        'merged_energy_data_processed.csv',
        'merged_consumer_data_processed.csv',
        'merged_finance_data_processed.csv',
        'merged_healthcare_data_processed.csv',
        'merged_industrial_data_processed.csv',
        'merged_shanghai_index_data_processed.csv',
        'merged_technology_data_processed.csv'
    ]

    # 遍历文件并处理
    for file in files:
        eval_model(os.path.join(data_path, file), best_clf, vectorizer)
