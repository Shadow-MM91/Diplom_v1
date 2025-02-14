import pandas as pd
import os
import psycopg2 as ps

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')
csv_file_store_path = AIRFLOW_HOME + '/dags/data/supermarket_sales - Sheet1.csv'

def is_accessible(path, mode='r'):
    """
    Проверка, является ли файл или папка из `path`
    доступным для работы в предоставленным `mode` формате.
    """
    try:
        f = open(path, mode)
        f.close()
    except IOError:
        return False
    return True

def clear_data(df):
    # Убираем в столбце City 'Nan' и ''. заполняем по столбцу branch
    city_der = {'A': 'Yangon',
                'B': 'Mandalay',
                'C': 'Naypyitaw',
                'D': 'Sittwe',
                'E': 'Myitkyina'}
    df = df.fillna('')
    for i in range(len(df)):
        df.iat[i, 2] = city_der[df.iat[i, 1]]
    return df

def branch(df, hook) -> None:
    branch = pd.DataFrame(pd.Series(df['branch'].unique(), name='branch'))  # Исправил
    branch.index += 1
    branch.to_sql(name='branch', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')

def city(df, hook):
    city = pd.DataFrame(pd.Series(df['city'].unique(), name='city'))
    city.index += 1
    city.to_sql(name='city', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')

def customer_type(df, hook):
    customer_type = pd.DataFrame(pd.Series(df['customer_type'].unique(), name='customer_type'))
    customer_type.index += 1
    customer_type.to_sql(name='customer_type', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')

def gender(df, hook):
    gender = pd.DataFrame(pd.DataFrame(pd.Series(df['gender'].unique(), name='gender')))
    gender.index += 1
    gender.to_sql(name='gender', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')

def product_line(df, hook):
    product_line = pd.DataFrame(pd.Series(df['product_line'].unique(), name='product_line'))
    product_line.index += 1
    product_line.to_sql(name='product_line', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')

def payment(df, hook):
    payment = pd.DataFrame(pd.Series(df['payment'].unique(), name='payment'))
    payment.index += 1
    payment.to_sql(name='payment', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace')

def fact_sales_branch(df, hook):
    conn = hook.get_conn()  # Установить соединение с базой данных
    cursor = conn.cursor()  # Вызываем класс позволяющий выполнять команды базе данных
    cursor.execute("""SELECT * FROM nds.branch;""")  # Мотод запускающий команду или запрос
    branch = dict(cursor.fetchall())  # Возвращаем список со всеми строками результата запроса затем преобразуем в словарь (ключ-значение)
    cursor.execute("""SELECT * FROM nds.city;""")  # Мотод запускающий команду или запрос
    city = dict(cursor.fetchall())  # Возвращаем список со всеми строками результата запроса затем преобразуем в словарь (ключ-значение)
    cursor.execute("""SELECT * FROM nds.customer_type;""")  # Мотод запускающий команду или запрос
    customer_type = dict(cursor.fetchall())  # Возвращаем список со всеми строками результата запроса затем преобразуем в словарь (ключ-значение)
    cursor.execute("""SELECT * FROM nds.gender;""")  # Мотод запускающий команду или запрос
    gender = dict(cursor.fetchall())  # Возвращаем список со всеми строками результата запроса затем преобразуем в словарь (ключ-значение)
    cursor.execute("""SELECT * FROM nds.product_line;""")  # Мотод запускающий команду или запрос
    product_line = dict(cursor.fetchall())  # Возвращаем список со всеми строками результата запроса затем преобразуем в словарь (ключ-значение)
    cursor.execute("""SELECT * FROM nds.payment;""")  # Мотод запускающий команду или запрос
    payment = dict(cursor.fetchall())  # Возвращаем список со всеми строками результата запроса затем преобразуем в словарь (ключ-значение)
    cursor.close()  # Закрываем курсор (класс)
    conn.close()  # Закрыть соединение с базой данных
    df['date'] = pd.to_datetime(df['date'], format="%m/%d/%Y")
    df['time'] = pd.to_datetime(df['time'], format="%H:%M").dt.time
    df['branch'] = df['branch'].map({v: k for k, v in branch.items()})
    df['city'] = df['city'].map({v: k for k, v in city.items()})
    df['customer_type'] = df['customer_type'].map({v: k for k, v in customer_type.items()})
    df['gender'] = df['gender'].map({v: k for k, v in gender.items()})
    df['product_line'] = df['product_line'].map({v: k for k, v in product_line.items()})
    df['payment'] = df['payment'].map({v: k for k, v in payment.items()})
    df['unit_price'] = df['unit_price'].astype(float)
    df['quantity'] = df['quantity'].astype(float)
    df['tax_5%'] = df['tax_5%'].astype(float)
    df['total'] = df['total'].astype(float)
    df['payment'] = df['payment'].astype(float)
    df['cogs'] = df['cogs'].astype(float)
    df['gross_margin_percentage'] = df['gross_margin_percentage'].astype(float)
    df['gross_income'] = df['gross_income'].astype(float)
    df['rating'] = df['rating'].astype(float)
    df.index += 1
    df.to_sql(name='fact_sales_branch', con=hook.get_sqlalchemy_engine(), schema='nds', if_exists='replace', index=False)

def postgresql_to_dataframe(hook, select_query, column_names):
    """
    Функция преобразует запрос SELECT в DataFrame
    """
    conn = hook.get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, ps.DatabaseError) as error: # Обработка ошибок
        print("Error: %s" % error)
        # cursor.close()
        return 1
    # Получаем кортежи
    tupples = cursor.fetchall()
    cursor.close()
    # Переводим кортеж в DataFrame
    df = pd.DataFrame(tupples, columns=column_names)
    return df

def source_processing_1(hook):
    df = pd.read_csv(csv_file_store_path)
    df.columns = [column_title.lower().replace(' ', '_') for column_title in df.columns]
    branch(df, hook)
    city(df, hook)
    customer_type(df, hook)
    gender(df, hook)
    payment(df, hook)
    product_line(df, hook)
    fact_sales_branch(df, hook)
    os.remove(csv_file_store_path)

def source_processing_2(hook):
    column_names = ['id', 'invoice_id', 'branch', 'city', 'customer_type',
                    'gender', 'product_line', 'unit_price', 'quantity',
                    'tax_5%', 'total', 'date', 'time', 'payment', 'cogs',
                    'gross_margin_percentage', 'gross_income', 'rating']
    column_names_1 = ['last_value_id']

    df_id = postgresql_to_dataframe(hook, "SELECT * FROM stg.temp_var", column_names_1)
    if df_id.empty == False:  # Проверка на присутствие данных в DataSet
        df_id = df_id["last_value_id"].tolist()  # Преобразование значенией в список
        df = postgresql_to_dataframe(hook, "SELECT * FROM stg.test_data_gener",column_names)  # Запрос к Базе данных на тестовые данные
        temp = df.index[df["id"] == df_id[0]].tolist()  # Выводим значение индекса строки отфильтрованного по значению из столбца 'id', преобразуем в список.
        df = df.loc[temp[0]:]  # Делаем новый срез DataSet от последней строки последнего обработанного среза до конца
        df_id = df.pop('id')  # Удаляем столбец 'id' из датасета df и одновременно формеруем список значений 'id'
        df_id = df_id.tail(1)  # Берём последнее значение списка
        df_id = df_id.rename('last_value_id')
        df_id.to_sql(name='temp_var', con=hook.get_sqlalchemy_engine(), schema='stg', if_exists='replace', index=False)  # Перезаписываем новое значение 'id' последней строки DataFrame в базу данных таблица 'temp_var'
        df = clear_data(df)  # Убираем в столбце City 'Nan' и ''. заполняем по столбцу branch
        df.columns = [column_title.lower().replace(' ', '_') for column_title in df.columns]
        branch(df, hook)
        city(df, hook)
        customer_type(df, hook)
        gender(df, hook)
        payment(df, hook)
        product_line(df, hook)
        fact_sales_branch(df, hook)
    else:
        df = postgresql_to_dataframe(hook, "SELECT * FROM stg.test_data_gener", column_names)
        if df.empty == False:
            df_id = df.pop('id')
            df_id = df_id.tail(1)
            df_id = df_id.rename('last_value_id')
            df_id.to_sql(name='temp_var', con=hook.get_sqlalchemy_engine(), schema='stg', if_exists='replace', index=False)
            df = clear_data(df)
            df.columns = [column_title.lower().replace(' ', '_') for column_title in df.columns]
            branch(df, hook)
            city(df, hook)
            customer_type(df, hook)
            gender(df, hook)
            payment(df, hook)
            product_line(df, hook)
            fact_sales_branch(df, hook)

def nds(hook):
    if is_accessible(csv_file_store_path):
        source_processing_1(hook)
    else:
        source_processing_2(hook)
