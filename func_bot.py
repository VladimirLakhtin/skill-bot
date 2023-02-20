import sqlite3
import difflib


#Конект с БД
connection = sqlite3.connect("db.db")
cursor = connection.cursor()


#Список данных из бд
def main_get(tables: list(), columns=[], condition='', is_one=False) -> list():

    # WHERE param
    if condition:
        condition = 'WHERE ' + condition + ' '

    # SELECT param
    if len(columns) > 1:
        columns_text = ', '.join(columns)
    elif len(columns) == 1:
        columns_text = columns[0]
    else:
        columns_text = '*'

    # FROM param
    if len(tables) == 2:
        tables = tables[0] + ' INNER JOIN ' + tables[1] + ' ON teacher_id == teachers.id'
    else:
        tables = tables[0]

    # request
    request = f"""SELECT {columns_text} FROM {tables} {condition}"""
    cursor.execute(request)
    records = cursor.fetchone() if is_one else cursor.fetchall()
    # return

    if is_one:
        if len(columns) == 1:
            return records[0]
        else:
            return [rec for rec in records]
    else:
        if len(columns) > 1:
            res = []
            for i in range(len(columns)):
                res.append([rec[i] for rec in records])
            return res
        else:
            return [rec[0] for rec in records]


#Берём информацию по студенту или куратору по id кнопке
def get_info_list(record_id: str, table: str):
    columns = [f'{table}.id', f'{table}.name', 'direction', f'{table}.tg_username']
    tables = ['teachers']
    if table == 'students':
        columns.append('score')
        columns.append('teachers.name')
        tables = ['students', 'teachers']
    list_info = main_get(
        tables=tables, 
        columns=columns, 
        condition=f"{table}.id == {record_id}",
        is_one=True
    )
    text_info = f"ID - {list_info[0]}\nИмя - {list_info[1]}\nПрофессия - {list_info[2]}\nUser-name - {list_info[3]}"
    columns = ['User-id','Имя', 'User-name', 'Профессия']
    if table == 'students':
        text_info += f'\nSkillCoins - {list_info[4]}\nКуратор - {list_info[5]}'
        columns.append('Куратор')
        columns.append('SkillCoins')

    return text_info, columns


#Удаляем человека из бд по id
def remove_record(record_id: str, table: str) -> None:
    cursor.execute(f"""DELETE FROM {table} WHERE id = {record_id}""")
    connection.commit()


#Добавляем тип профессии
def add_record(table: str, params: dict) -> None:
    values = [str(p) if type(p) != str else p for p in params.values()]
    request = f"""INSERT INTO {table} ({', '.join(params.keys())}) VALUES ({', '.join(values)})"""
    cursor.execute(request)
    connection.commit()


#Возвращаем список поиска студентов или кураторов при помощи вероятности совпадения букв в фамилии и в имени
def get_search_results(table, name):
    result_id, result_names = [], []
    prob = 0.7
    id_list, names_list = main_get(tables=[table], columns=['id', 'name'])
    names_split_list = [i.split() for i in names_list]
    name = name.lower().split()
    for i, cur_name in enumerate(names_split_list):
        surname_human = cur_name[0].lower()
        name_human = cur_name[1].lower()
        if len(name) == 1:
            matcher_surname = difflib.SequenceMatcher(None, name[0], surname_human).ratio()
            matcher_name = difflib.SequenceMatcher(None, name[0], name_human).ratio()
            if (matcher_surname >= prob or matcher_name>= prob):
                result_id.append(id_list[i])
                result_names.append(cur_name[0] + ' ' + cur_name[1])
        else:
            matcher_surname = difflib.SequenceMatcher(None, name[0], surname_human).ratio()
            matcher_name = difflib.SequenceMatcher(None, name[1], name_human).ratio()
            matcher_surname_back = difflib.SequenceMatcher(None, name[0], name_human).ratio()
            matcher_name_back = difflib.SequenceMatcher(None, name[1], surname_human).ratio()
            if (matcher_surname >= prob or matcher_name>= prob) or (matcher_surname_back >= prob or matcher_name_back >= prob):
                result_id.append(id_list[i])             
                result_names.append(" ".join(cur_name))
    return result_id, result_names


def update_record(table: str, rec_id, columns: dict) -> None:
    col_val_text = ''
    for col, val in columns.items():
        col = col.replace('-', '_')
        col_val_text += f"{col} = " + (f"{val}" if type(val) == int else f"'{val}'")
    request = f"UPDATE {table} SET {col_val_text} WHERE id = {rec_id}"
    cursor.execute(request)
    connection.commit()

if __name__ == "__main__":
    update_record(table='students', rec_id=1, columns={'score': 657})