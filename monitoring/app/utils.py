

def calculate_points(result, min_r, max_r, koef_min, koef_top):
    if min_r > max_r:
      max_r, min_r = min_r, max_r
    if min_r == max_r:
      return 0
    price = 100 / (max_r - min_r)
    shift = 0
    if result > max_r:
        shift = result - max_r
        result = max_r
    rating = (result - min_r) / (max_r - min_r) * 10 * koef_min + shift * price * koef_top
    return max(round(rating, 2), 0)


# import pandas as pd
# from datetime import datetime
#
# def get_filled_data(data):
#     # Создание DataFrame из первой пары массивов
#     df1 = pd.DataFrame(data[0])
#
#     # Создание DataFrame из второй пары массивов
#     df2 = pd.DataFrame(data[1])
#
#     # Объединение по меткам (label) с сохранением соответствия
#     result_df = pd.merge(df1, df2, on='x', how='outer')
#
#     # Преобразование строк в datetime
#     #result_df['x'] = pd.to_datetime(result_df['x'], format='%m-%d')
#
#     # Сортировка по значениям label
#     result_df.sort_values(by='x', inplace=True)
#
#     # Замена NaN на None
#     result_df = result_df.where(pd.notna(result_df), None)
#
#     # Получение массивов из DataFrame
#     label_result = result_df['x'].tolist()
#     data1_result = result_df['y_x'].tolist()
#     data2_result = result_df['y_y'].tolist()
#     data[0]['x'] = data1_result
#     data[1]['x'] = data2_result
#
#     return data, label_result
#
