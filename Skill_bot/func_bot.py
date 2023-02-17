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
    if len(columns) > 1 and not is_one:
        list_of_columns = []
        for i in range(len(columns)):
            if len(records) > 1:
                list_of_columns.append([rec[i] for rec in records])
            else:
                list_of_columns.append(records[0][i])
        return list_of_columns
    elif len(columns) == 1:
        return [rec[0] for rec in records]
    return records


#Берём информацию по студенту или куратору по id кнопке
def get_info_list(record_id: str, table: str) -> list():
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
    text_info = f"ID - {list_info[0]}\nИмя - {list_info[1]}\nПрофессия - {list_info[2]}\nТГ-name - {list_info[3]}"
    if table == 'students':
        text_info += f'\nSkillCoins - {list_info[4]}\nКуратор - {list_info[5]}'
    return text_info


#Удаляем человека из бд по id
def remove_record(record_id: str, table: str) -> None:
    cursor.execute(f"""DELETE FROM {table} WHERE id = {record_id}""")
    connection.commit()


#Добавляем тип профессии
def add_record(table: str, params: dict) -> None:
    values = [str(p) if type(p) != str else p for p in params.values()]
    request = f"""INSERT INTO {table} ({', '.join(params.keys())}) VALUES ({', '.join(values)})"""
    print(request)
    cursor.execute(request)
    connection.commit()


#Возвращаем список поиска студентов или кураторов при помощи вероятности совпадения букв в фамилии и в имени
#TODO: Доработать
def search_db_student_teacher(table, name):
    lsit_name_search_human_probability = []
    list_name_search_human_100_probability = []
    try:
        list_name = name_list_db_student_and_teacher(table)[0]
        list_name_search = [i.split() for i in list_name]
        name_1 = name.lower().split()
        for i in list_name_search:
            surname_human = i[0].lower()
            name_human = i[1].lower()
            surname_human_back = i[1].lower()
            name_human_back = i[0].lower()
            if len(name.split()) == 1:
                matcher_surname = difflib.SequenceMatcher(None, name_1[0], surname_human)
                matcher_name = difflib.SequenceMatcher(None, name_1[0], name_human)
                matcher_surname_back = difflib.SequenceMatcher(None, name_1[0], surname_human_back)
                matcher_name_back = difflib.SequenceMatcher(None, name_1[0], name_human_back)
            else:
                matcher_surname = difflib.SequenceMatcher(None, name_1[0], surname_human)
                matcher_name = difflib.SequenceMatcher(None, name_1[1], name_human)
                matcher_surname_back = difflib.SequenceMatcher(None, name_1[0], surname_human_back)
                matcher_name_back = difflib.SequenceMatcher(None, name_1[1], name_human_back)
            if ((matcher_surname.ratio() >= 0.35 or matcher_name.ratio() >= 0.35) and (matcher_name.ratio() < 0.75 or matcher_surname.ratio() < 0.75)) or ((matcher_surname_back.ratio() >= 0.35 or matcher_name_back.ratio() >= 0.35) and (matcher_name_back.ratio() < 0.75 or matcher_surname_back.ratio() < 0.75)) :
                lsit_name_search_human_probability.append(" ".join(i))
            elif (matcher_name.ratio() >= 0.83 and matcher_surname.ratio() >= 0.83) or (matcher_name_back.ratio() >= 0.83 and matcher_surname_back.ratio() >= 0.83):
                list_name_search_human_100_probability.append(" ".join(i))
        if len(list_name_search_human_100_probability) == 1:
            return list_name_search_human_100_probability
        else:
            return lsit_name_search_human_probability
    except Exception:
        return lsit_name_search_human_probability

if __name__ == "__main__":
    print(main_get(tables=['teachers'], columns=['direction']))