import pandas as pd
import random
import string
import numpy as np
from datetime import datetime

def test_data_gener (hook):

    t_head = ['invoice_id', 'branch','city','customer_type',
          'gender','product_line','unit_price','quantity',
          'tax_5%','total','date','time','payment','cogs',
          'gross_margin_percentage','gross_income','rating']
    df = pd.DataFrame(columns=t_head)

    for i in range(10):
          # 'invoice_id' - генерим значения
          der = "".join(random.choices(string.digits, k=3))
          der_1 = "".join(random.choices(string.digits, k=2))
          der_2 = "".join(random.choices(string.digits, k=4))
          summ = der + "-"+ der_1 + "-"+ der_2

          # 'branch' и 'city' - генерим значения
          branch = ['A','B','C','D','E']
          branch = "".join(random.choices(branch, k=1))
          if branch == 'A':
            city = ['Yangon', '', 'NULL']
            city = "".join(random.choices(city, k=1))
            if city == 'NULL':
              city = np.nan
          if branch == 'B':
            city = ['Mandalay', '', 'NULL']
            city = "".join(random.choices(city, k=1))
            if city == 'NULL':
              city = np.nan
          if branch == 'C':
            city = ['Naypyitaw', '', 'NULL']
            city = "".join(random.choices(city, k=1))
            if city == 'NULL':
              city = np.nan
          if branch == 'D':
            city = ['Sittwe', '', 'NULL']
            city = "".join(random.choices(city, k=1))
            if city == 'NULL':
              city = np.nan
          if branch == 'E':
            city = ['Myitkyina', '', 'NULL']
            city = "".join(random.choices(city, k=1))
            if city == 'NULL':
              city = np.nan

          # 'customer_type' - генерим значения
          customer_type = ['Member','Normal']
          customer_type = "".join(random.choices(customer_type, k=1))

          # 'gender' - генерим значения
          gender = ['Female','Male']
          gender = "".join(random.choices(gender, k=1))

          # 'product_line' - генерим значения
          product_line = ['Health and beauty',
                          'Electronic accessories',
                          'Home and lifestyle',
                          'Sports and travel',
                          'Food and beverages',
                          'Fashion accessories']
          product_line = "".join(random.choices(product_line, k=1))

          # 'unit_price', 'quantity', 'tax_5%', 'total', 'rating' - генерим значения
          rating = random.uniform(1.0, 10.0)
          unit_price = round(random.uniform(10.0, 100.0),2)
          quantity = round(random.uniform(1.0, 10.0))
          cogs = unit_price * quantity
          tax_5 = cogs * 0.05
          total = cogs + tax_5
          rating = "{:.1f}".format(rating)
          quantity = "{:.0f}".format(quantity)
          unit_price = "{:.2f}".format(unit_price)
          cogs = "{:.2f}".format(cogs)
          tax_5 = "{:.4f}".format(tax_5)
          total = "{:.4f}".format(total)

          # 'payment' - генерим значения
          payment = ['Ewallet','Cash','Credit card']
          payment = "".join(random.choices(payment, k=1))

          # 'date', 'time' - генерим значения
          start_date = datetime(2019, 6, 9)
          end_date = datetime(2019, 3, 10)
          res = pd.date_range(min(start_date, end_date),
                              max(start_date, end_date)).strftime('%m/%d/%Y').tolist()
          for j in range(len(res)):
            res[j] = res[j].replace("/0", "/").lstrip("0")
          date = "".join(random.choices(res, k=1))

          time1 = [i.strftime("%H:%M") for i in pd.date_range("10:00", "20:59", freq="1min").time]
          time1 = "".join(random.choices(time1, k=1))

          new_row = {'invoice_id': summ, 'branch': branch,'city': city,'customer_type': customer_type,
                    'gender': gender,'product_line': product_line,'unit_price': unit_price,'quantity': quantity,
                    'tax_5%': tax_5,'total': total,'date': date,'time': time1,'payment': payment,'cogs': cogs,
                    'gross_margin_percentage': '4.761905','gross_income': tax_5,'rating': rating}
          df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_sql(name='test_data_gener', con=hook.get_sqlalchemy_engine(), schema='stg', if_exists='append', index=False)