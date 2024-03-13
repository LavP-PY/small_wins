import os
import csv
from prettytable import PrettyTable
import pandas as pd


class PriceMachine():

    def __init__(self):
        # self.data = []
        # self.result = ''
        # self.name_length = 0
        self.groceries_list = []
        self.head = ['Наименование', 'Цена', 'Вес', 'Файл', 'Цена за кг.']
        self.load_prices() # это сюда добавлено, чтобы считывание происходило сразу, как только создаётся объект класса,
        # и можна сразу переходить к поиску товара в прайсах или созданию файла html

    def load_prices(self, file_path=''):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт
                
            Допустимые названия для столбца с ценой:
                розница
                цена
                
            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка
        '''
        names = ["название", "продукт", "товар", "наименование"]
        prices = ["цена", "розница"]
        weights = ["фасовка", "масса", "вес"]
        all_files = []
        # ищем прайс-листы с нужными названиями
        for root, dirs, files in os.walk('loader', topdown=False):
            for file in files:
                if file.endswith('.csv'):
                    file_price = os.path.join(file)
                    price_pattern = 'price'
                    if price_pattern in file_price:
                        all_files.append(file_price)
        # делаем выборку необходимы столбцов из наших прайсов
        for file_with_price in all_files:
            products_name = []
            products_price = []
            products_weight = []

            with open(f'loader/{file_with_price}', newline='', encoding='utf-8') as datas:
                dic_read = csv.DictReader(datas, delimiter=',')
                for row in dic_read:
                    for keydict in row:
                        if keydict in names:
                            name_food = row[keydict]
                            products_name.append(name_food)
                        elif keydict in prices:
                            price_food = row[keydict]
                            products_price.append(price_food)
                        elif keydict in weights:
                            weight_food = row[keydict]
                            products_weight.append(weight_food)
                # записываем все товары в один общий документ, для последующей работы с ним
                for j in range(len(products_name)):
                    self.groceries_list.append({self.head[0]: products_name[j],
                                                self.head[1]: products_price[j],
                                                self.head[2]: products_weight[j],
                                                self.head[3]: file_with_price,
                                                self.head[4]: round(int(products_price[j]) / int(products_weight[j]), 2)})
        # Сортируем полученный список словарей
        self.groceries_list.sort(key=lambda item: (item["Наименование"]))
        # Записываем промежуточный общий файл csv, чтобы потом списать информацию из него в html
        with open('common_price.csv', mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['№', 'Наименование', 'Цена', 'Вес', 'Файл', 'Цена за кг.']
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()
            for i, item in enumerate(self.groceries_list, 1):
                item['№'] = i
                writer.writerow(item)

    # def _search_product_price_weight(self, headers):
    #     ЗАЧЕМ ЭТОТ МЕТОД???? О НЁМ даже в задании ничего не сказано(((
    #     '''
    #         Возвращает номера столбцов
    #     '''
    #     pass

    def export_to_html(self, fname='output.html'):
        groceries_list_pd_csv = pd.read_table('common_price.csv', sep=',', index_col=0)
        groc_str = ['<HTML>']
        groc_str.append('<HEAD><TITLE>GROCERIES_PRICE</TITLE></HEAD>')
        groc_str.append('<BODY>')
        groc_str.append(groceries_list_pd_csv.to_html())
        groc_str.append('</BODY></HTML>')
        html_groceries = ''.join(groc_str)

        html_file = open(fname, 'w', encoding="utf-8")
        html_file.write(html_groceries)
        html_file.close()

    def find_text(self):
        # Создаём список продуктов, которых ищет пользователь, и создаём список стоп-слов
        # здесь я решил так лучше, иметь несколько стоп-слов, а то поиск на русском, а отмена на ангийском...
        dict_users_search_for = []
        list_to_cancel = ['exit', 'выход', 'отмена']
        # запускаем цикл непрерывной работы
        while True:
            users_data = input('Please, Enter a product name to looking for.\n'
                               f'(Note: to cancel, enter some word from list - {", ".join(list_to_cancel)}):')
            if users_data.lower() in list_to_cancel:
                break

            for row in self.groceries_list:
                if users_data.lower() in row['Наименование'].lower():
                    dict_users_search_for.append(row)

            # Сортируем список словарей найденных продуктов
            dict_users_search_for.sort(key=lambda item: (item["Цена за кг."], ["Наименование"]))

            # Записываем его в отдельный файл, чтобы добавить нумерацию строк
            with open('searching.csv', mode='w', newline='', encoding='utf-8') as csv_out:
                fieldnames = ['№', 'Наименование', 'Цена', 'Вес', 'Файл', 'Цена за кг.']
                writer = csv.DictWriter(csv_out, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                for i, item in enumerate(dict_users_search_for, 1):
                    item['№'] = i
                    writer.writerow(item)

            # Создаём список СТРОКОВЫЙ для последующего вывода на консоль
            # Потому что красивая таблица модуля PrettyTable принимает строки
            list_users_search_for = []
            with open('searching.csv', 'r', newline='', encoding='utf-8') as csv_in:
                read = csv.reader(csv_in, delimiter=';')
                for line in read:
                    list_users_search_for.append(line)
            # Выводим красивую таблицу на консоль из СТРОКОВОГО списка
            for line in list_users_search_for:
                table = PrettyTable()
                table.field_names = list_users_search_for[0]
                table.add_rows(list_users_search_for[1:len(list_users_search_for)])
            print(table)

            if len(dict_users_search_for) == 0:
                print('\nОшибка! Запрашиваемого товара нет в прайсах\n')

            # Обнуляем список поиска, чтобы каждый раз отображалась таблица от нового поискового слово
            dict_users_search_for = []



pm = PriceMachine()
pm.find_text()
# print(pm.export_to_html())

