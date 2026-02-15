import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import classification_report

pd.set_option('display.max_columns', None)

train = pd.read_csv('train.csv')
# print(train)
train = train.iloc[:, 1:13]  # Удаление Loan_ID

na = train.isna().sum().sort_values(ascending=False)  # Поиск количества NaN-значений для каждого изи признаков
# print(na)

# Замена NaN значений на средние
for column, na_count in na.items():
    if na_count > 0:
        if train.dtypes[column] == 'float64':
            train[column] = train[column].fillna(float(int(train[column].mean())))  # mean для числовых признаков
        else:
            train[column] = train[column].fillna(train[column].mode()[0])  # мода для категориальных

# print(train.isna().sum().sort_values(ascending=False))

# Замена категориальных признаков на числовое представление
categorical_features = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 'Property_Area', 'Loan_Status']
for feature in categorical_features:
    train[feature] = LabelEncoder().fit_transform(train[feature])

# print(train)

stats = train.describe()  # Статистический анализ датасета
# print(stats)

# отделение признаков от меток классов
X = train.iloc[:, 1:11].to_numpy()
Y = train.iloc[:, 11].to_numpy()

sizes = np.arange(start=0.05, stop=1, step=0.05)


def score_size(m, train_x, test_x, train_y, test_y):
    m.fit(train_x, train_y)
    scores.append(m.score(test_x, test_y))


methods = [GaussianNB(), tree.DecisionTreeClassifier(), SVC(), LinearDiscriminantAnalysis()]
score_size_df = pd.DataFrame()
score_size_df['size'] = sizes

# Случайные состояния
states = [0, 30410, 8723]
for state in states:
    for method in methods:
        scores = []
        for size in sizes:
            X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=size,
                                                                random_state=state)  # Подготовка обучающей и тестовой выборки
            score_size(method, X_train, X_test, y_train, y_test)  # вычисление точности

        score_size_df[method] = scores
        # plt.plot(sizes, scores)
        # plt.title(str(method))
        # plt.xlabel("Размер тестовой выборки")
        # plt.ylabel("Score")
        # plt.show()

    print(f"Random state = {state}")

    # Поиск размеров выборок для каждого метода, при которых точность наилучшая
    max_values = {}
    for method in methods:
        max_index = score_size_df[method].idxmax()
        max_values[method] = {
            'max_value': score_size_df.loc[max_index, method],
            'size': score_size_df.loc[max_index, 'size']
        }

    best_method = GaussianNB()
    best_score = 0
    best_size = None

    # Поиск наилучшей комбинации метода и размера выборки для каждого из random_state
    for method, values in max_values.items():
        if values['max_value'] > best_score:
            best_method = method
            best_score = values['max_value']
            best_size = values['size']
        # print(f"{method}: max_value = {values['max_value']}, size = {values['size']}")

    print(f"Best method = {best_method}, best size = {best_size}")

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=best_size, random_state=state)
    best_method.fit(X_train, y_train)
    y_pred = best_method.predict(X_test)
    print(classification_report(y_test, y_pred))  # Анализ по Precision, Recall, F1
    print("------------------")
