import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import folium


n_rooms = ['студия','1', '2',  '3', '4','5', '6','7', '8', '9','10 и больше','свободная планировка']


def plot_numerical_feature(df: pandas.DataFrame,
                           feature: str,
                           max_quantile: float = None,
                           figsize: tuple[int, int] = None,
                           title: str = None) -> None:
    """
    Строит графики распределения числовых признаков
    - ящик с усами
    - гистограмма
    
    Параметры
    ----------
    df - датафрейм для подсчета
    feature - признак
    max_quantile - значение признака будет рассматриваться от минимума до max_quantile квартиля
    figsize - размер графика
    title - заголовок графика
    """
    feature_values = df[feature]
    fig, axes = plt.subplots(1, 2, figsize=(20, 8) if not figsize else figsize)

    sns.boxplot(x=feature_values, ax=axes[0])

    if max_quantile:
        mask = df[feature].quantile(max_quantile)
        feature_values = feature_values[feature_values < mask]

    sns.histplot(x=feature_values, kde=True, ax=axes[1])

    axes[1].set_ylabel('Количество')
    axes[0].set_xlabel('Значение')
    axes[1].set_xlabel('Значение')

    if title:
        plt.suptitle(title, fontsize=15)
    else:
        plt.suptitle(feature, fontsize=15)
    sns.despine()
    plt.show()
    

def get_nulls(df: pandas.DataFrame) -> None:
    """
    Функция для подсчета количества и процента
    пропущенных значений признаков.
    
    Параметры
    ----------
    df - датафрейм для подсчета

    Возвращает
    -------
    nulls - количество пропущенных значений в признаках
    nulls_pct - процент пропущенных значений в признаках
    """
    nulls = df.isnull().sum()[lambda x: x > 0].sort_values(ascending=False)
    nulls = nulls.rename_axis('Признак')
    
    nulls_pct = nulls.reset_index(name='Процент')
    nulls_pct['Процент'] = (nulls_pct['Процент'] / len(df)).round(3)
    
    nulls = nulls.reset_index(name='Количество')
    return nulls, nulls_pct


def plot_nulls(df: pandas.DataFrame,
               figsize: tuple[int, int] = (25, 7),
               title_size: int = 15) -> None:
    """
    Строит график количества и процента
    пропущенных значений признаков.
    """
    nulls, nulls_pct = get_nulls(df)

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    fig1 = sns.barplot(x='Признак', y='Количество', data=nulls, ax=axes[0])
    fig1.bar_label(fig1.containers[0])

    fig2 = sns.barplot(x='Признак', y='Процент', data=nulls_pct, ax=axes[1])
    fig2.bar_label(fig2.containers[0])

    for item in axes[0].get_xticklabels():
        item.set_rotation('vertical')
    for item in axes[1].get_xticklabels():
        item.set_rotation('vertical')

    fig.suptitle('Пропущенные значения в признаках', fontsize=title_size)
    axes[0].set(xlabel=None)
    axes[0].set_title('Количество', fontsize=title_size - 2)
    axes[1].set(xlabel=None)
    axes[1].set_title('В процентах', fontsize=title_size - 2)
    sns.despine(fig)
    plt.show()
    

def plot_pie_columns(df: pandas.DataFrame,
                     name: str,
                     n_rows: int = 1) -> None:
    """
    Строит круговую диаграмму значений признака
    
    Параметры
    ----------
    df - набор данных
    name - название признака
    """
    colours = {'есть': 'C2', 'нет': 'C0', 'не указано': 'C3'}
    features = df.filter(like=name, axis=1)
    if n_rows == 1:
        fig, axes = plt.subplots(1,
                                 features.shape[1],
                                 figsize=(features.shape[1] * 3, 4))
    else:
        fig, axes = plt.subplots(n_rows,
                                 features.shape[1] // n_rows,
                                 figsize=(features.shape[1] * 3 // 2,
                                          4 * n_rows))
    plt.suptitle(name, y=0.9)
    for ind in range(features.shape[1]):
        title = features.columns[ind].replace(name, '').replace('_',
                                                                ' ').strip()

        values = features.iloc[:, ind].map({1: 'есть', 0: 'нет'})
        values = values.fillna('не указано').value_counts()

        if n_rows == 1:
            axes[ind].pie(values,
                          labels=values.index,
                          autopct='%.2f',
                          colors=[colours[key] for key in values.index])
            axes[ind].set_title(title)

        else:
            scaler = features.shape[1] // n_rows
            axes[ind // scaler, ind % scaler].pie(
                values,
                labels=values.index,
                autopct='%.2f',
                colors=[colours[key] for key in values.index])
            axes[ind // scaler, ind % scaler].set_title(title)

    plt.tight_layout()
    plt.show()
    
 
def show_circles_on_map(data: pandas.DataFrame,
                        latitude_column: str,
                        longitude_column: str,
                        color: str) -> None:
    """
    Функция для рисования координат.
    
    Параметры
    ----------
    data - набор данных
    latitude_column - название столбца, в котором содержится широта
    longitude_column - название столбца, в котором содержится долгота
    color - цвет
    """

    location = (data[latitude_column].mean(), data[longitude_column].mean())
    m = folium.Map(location=location)

    for _, row in data.iterrows():
        folium.Circle(radius=100,
                      location=(row[latitude_column], row[longitude_column]),
                      color=color,
                      fill_color=color,
                      fill=True).add_to(m)

    return m
    
    
def plot_feature_for_rooms(df: pandas.DataFrame, feature: str) -> None:
    """
    Функция для построения боксплота признака в зависимости от количества комнат в квартире.
    
    Параметры
    ----------
    df - набор данных
    feature - признак
    """
    fig, axes = plt.subplots(4, 3, figsize=(20, 16))
    plt.suptitle(
        f"{feature.replace('_',' ')} в зависимости от количества комнат", y=1)

    for n in range(len(n_rooms)):
        sns.boxplot(x=df[df['Количество_комнат'] == n_rooms[n]][feature],
                    ax=axes[n // 3, n % 3])
        axes[n // 3, n % 3].set_title(n_rooms[n])
    plt.tight_layout()
    plt.show()
    

def plot_feature_boxplot(df: pandas.DataFrame, feature: str):
    """
    Функция для построения боксплота признака.
    
    Параметры
    ----------
    df - набор данных
    feature - признак
    """
    sns.boxplot(x=df[feature])
    plt.title(f"{feature.replace('_',' ')}")
    plt.show()
