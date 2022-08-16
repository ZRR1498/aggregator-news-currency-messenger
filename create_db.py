from parse_news_currency_crypto import collect_news, collect_crypto, collect_currency


def create_tables(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users
                          (user_id SERIAL PRIMARY KEY,
                          user_name VARCHAR(50),
                          surname VARCHAR(50),
                          nickname VARCHAR(50),
                          email VARCHAR(50),
                          hash_password VARCHAR(200)
                          );''')

    connection.commit()


    with connection.cursor() as cursor:
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS messages
                          (id SERIAL PRIMARY KEY,
                          user_id INT REFERENCES users(user_id),
                          nickname VARCHAR(50),
                          user_text VARCHAR(1000),
                          date_time VARCHAR(30)
                          );''')

    connection.commit()


    with connection.cursor() as cursor:
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS tasks
                          (task_id SERIAL PRIMARY KEY,
                          user_id VARCHAR(50),
                          text_task VARCHAR(1000),
                          time_cr VARCHAR(30),
                          completed INTEGER
                          );''')

    connection.commit()


    with connection.cursor() as cursor:
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS exchange_currency
                          (currency_id SERIAL PRIMARY KEY,
                          currency_code VARCHAR(20),
                          amount VARCHAR(20),
                          currency_name VARCHAR(50),
                          currency_value VARCHAR(20),
                          date_time VARCHAR(30)
                          ); ''')

    connection.commit()


    with connection.cursor() as cursor:
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS exchange_crypto
                          (crypto_id SERIAL PRIMARY KEY,
                          crypto_name VARCHAR(50),
                          crypto_code VARCHAR(10),
                          price DECIMAL(30,20),
                          exchange_price VARCHAR(10),
                          capitalization VARCHAR(20),
                          volume VARCHAR(20),
                          exchange_per VARCHAR(20),
                          date_time VARCHAR(50)
                          );''')

    connection.commit()


    with connection.cursor() as cursor:
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS news(
                id SERIAL PRIMARY KEY,
                news VARCHAR,
                links VARCHAR,
                times VARCHAR,
                links_images VARCHAR);''')

    connection.commit()


def update_news(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            '''SELECT * FROM news ORDER BY 4 DESC LIMIT 1;''')

        last_time = cursor.fetchall()
        arr_news = collect_news()

        if last_time == []:
            for i in range(0, len(arr_news)):
                cursor.execute(
                    '''INSERT INTO news(news, links, times, links_images) VALUES (%s, %s, %s, %s);''',
                    (arr_news[i][0], arr_news[i][1], arr_news[i][2], arr_news[i][3]))
                connection.commit()

        else:
            last_time = last_time[0][3]
            for i in range(0, len(arr_news)):
                check_time = arr_news[i][2]
                if check_time > last_time:
                    cursor.execute(
                        '''INSERT INTO news(news, links, times, links_images) VALUES (%s, %s, %s, %s);''',
                                           (arr_news[i][0], arr_news[i][1], arr_news[i][2], arr_news[i][3]))
                    connection.commit()
                else:
                    continue


def update_crypto(connection):
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         '''DELETE FROM exchange_crypto;''')
    #     connection.commit()
    arr_crypto = collect_crypto()
    for i in range(1, len(arr_crypto)):
        with connection.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO exchange_crypto(crypto_name, crypto_code, price, exchange_price, capitalization, volume,
                exchange_per, date_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);''',
                (arr_crypto[i][0],arr_crypto[i][1], arr_crypto[i][2], arr_crypto[i][3], arr_crypto[i][4],
                 arr_crypto[i][5], arr_crypto[i][6], arr_crypto[i][7]))
            connection.commit()


def update_currency(connection):
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         '''DELETE FROM exchange_currency;''')
    #     connection.commit()
    arr_currency = collect_currency()
    for i in range(1, len(arr_currency)):
        with connection.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO exchange_currency(currency_code, amount, currency_name, currency_value, date_time)
                VALUES (%s, %s, %s, %s, %s);''', (str(arr_currency[i][0]), str(arr_currency[i][1]),
                                                  str(arr_currency[i][2]), str(arr_currency[i][3]),
                                                  str(arr_currency[i][4])))
            connection.commit()
