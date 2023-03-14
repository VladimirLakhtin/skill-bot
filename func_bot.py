from aiogram.utils.exceptions import MessageNotModified

from typing import List, Dict, Any, Tuple

import sqlite3
import difflib
from aiogram.types import InlineKeyboardMarkup

from create_bot import bot

# Connect db
connection = sqlite3.connect("db.db")
cursor = connection.cursor()

translate = {
    'tg_id': 'User-id',
    'tg_username': 'User-name',
    'name': 'Имя',
    'direction': 'Профессия',
    'score': 'SkillCoins',
    'title': 'Название',
    'description': 'Описание',
    'cost': 'Цена',
    'reward': 'Награда',
}


# Main function to get data
def main_get(tables: List, columns: List = [], condition: str = None, sort_by: str = None, is_one: bool = False) -> Any:
    # SELECT param
    if len(columns) > 1:
        columns_text = ', '.join(columns)
        one_col = False
    elif len(columns) == 1:
        columns_text = columns[0]
        one_col = True
    else:
        columns_text = '*'
        one_col = False

    # FROM param
    if len(tables) == 2:
        tables = tables[0] + ' INNER JOIN ' + tables[1] + ' ON teacher_id == teachers.id '
    else:
        tables = tables[0] + ' '

    # WHERE param
    condition = 'WHERE ' + condition + ' ' if condition else ''

    # ORDER BY param:
    sort_by = 'ORDER BY ' + sort_by if sort_by else ''

    # request
    request = f"""SELECT {columns_text} FROM {tables}{condition}{sort_by}"""
    cursor.execute(request)
    records = cursor.fetchone() if is_one else cursor.fetchall()

    # return
    if not records:
        return [[] for _ in columns]

    if is_one:
        if one_col:
            return records[0]
        else:
            return [rec for rec in records]
    else:
        if not one_col:
            res = []
            for i in range(len(records[0])):
                res.append([rec[i] for rec in records])
            return res
        else:
            return [rec[0] for rec in records]


# Get full info about a record
def get_info_list(record_id: str, table: str) -> (str, Dict[str, str]):
    tables = [table]
    text_info = ''
    columns = []
    if table == 'students':
        columns = ['students.id', 'students.name', 'teachers.direction', 'students.tg_username', 'students.score',
                   'teachers.name']
        tables = ['students', 'teachers']
    elif table == 'teachers':
        columns = ['id', 'name', 'direction', 'tg_username']
    elif table == 'awards':
        columns = ['id', 'title', 'cost', 'description']
    elif table == 'tasks':
        columns = ['id', 'title', 'reward', 'description']
    elif table == "admins":
        columns = ['id', 'name', 'tg_id']
    list_info = main_get(
        tables=tables,
        columns=columns,
        condition=f"{table}.id == {record_id}",
        is_one=True
    )
    if table == 'students':
        text_info = f"<b>Имя</b> - {list_info[1]}\n" \
                    f"<b>Профессия</b> - {list_info[2]}\n" \
                    f"<b>User-name</b> - {list_info[3]}\n" \
                    f"<b>SkillCoins</b> - {list_info[4]}\n" \
                    f"<b>Куратор</b> - {list_info[5]}"
        columns = [col.split('.')[-1] for col in columns]
    elif table == 'teachers':
        text_info = f"<b>Имя</b> - {list_info[1]}\n" \
                    f"<b>Профессия</b> - {list_info[2]}\n" \
                    f"<b>User-name</b> - {list_info[3]}"
    elif table == 'awards' or table == 'tasks':
        title = "Цена" if table == "awards" else "Награда"
        text_info = f"<b>Название</b> - {list_info[1]}\n" \
                    f"<b>Описание</b> - {list_info[3]}\n" \
                    f"<b>{title}</b>: {list_info[2]} SkillCoins"
    elif table == "admins":
        text_info = f"Информация об админе\n<b>Имя</b>: {list_info[1]}\n<b>TG-ID</b>: {list_info[2]}"
    columns = {key.replace('_', '-'): val for (key, val) in translate.items() if key in columns}
    return text_info, columns


# Delete a record
def remove_record(record_id: str, table: str) -> None:
    cursor.execute(f"""DELETE FROM {table} WHERE id = {record_id}""")
    connection.commit()


# Add a new record
def add_record(table: str, params: Dict) -> None:
    values = [str(p) if type(p) != str else p for p in params.values()]
    request = f"""INSERT INTO {table} ({', '.join(params.keys())}) VALUES ({', '.join(values)})"""
    cursor.execute(request)
    connection.commit()


# Search for similar names and surnames
def get_search_results(table: str, name: str, teacher_id: int = None) -> (List[str], List[str]):
    result_id, result_names = [], []
    prob = 0.7
    condition = f'teacher_id = {teacher_id}' if teacher_id else None
    id_list, names_list = main_get(tables=[table], columns=['id', 'name'], condition=condition)
    names_split_list = [i.split() for i in names_list]
    name = name.lower().split()
    for i, cur_name in enumerate(names_split_list):
        surname_human = cur_name[0].lower()
        name_human = cur_name[1].lower()
        if len(name) == 1:
            matcher_surname = difflib.SequenceMatcher(None, name[0], surname_human).ratio()
            matcher_name = difflib.SequenceMatcher(None, name[0], name_human).ratio()
            if (matcher_surname >= prob or matcher_name >= prob):
                result_id.append(id_list[i])
                result_names.append(cur_name[0] + ' ' + cur_name[1])
        else:
            matcher_surname = difflib.SequenceMatcher(None, name[0], surname_human).ratio()
            matcher_name = difflib.SequenceMatcher(None, name[1], name_human).ratio()
            matcher_surname_back = difflib.SequenceMatcher(None, name[0], name_human).ratio()
            matcher_name_back = difflib.SequenceMatcher(None, name[1], surname_human).ratio()
            if (matcher_surname >= prob or matcher_name >= prob) or (
                    matcher_surname_back >= prob or matcher_name_back >= prob):
                result_id.append(id_list[i])
                result_names.append(" ".join(cur_name))
    return result_id, result_names


# Update a record value
def update_record(table: str, rec_id, columns: Dict) -> None:
    col_val_text = ''
    for col, val in columns.items():
        col = col.replace('-', '_')
        col_val_text += f"{col} = " + (f"{val}" if type(val) == int else f"'{val}'")
    request = f"UPDATE {table} SET {col_val_text} WHERE id = {rec_id}"
    cursor.execute(request)
    connection.commit()


# Add SkillCoins to a student
def add_skillcoins(std_id, coins):
    cur_score = main_get(tables=['students'], columns=['score'], condition=f'students.id = {std_id}', is_one=True)
    new_score = int(cur_score) + int(coins)
    update_record(table='students', rec_id=std_id, columns={'score': new_score})


# Get top 10 students by SkillCoins
def get_top_std(teacher_id: int = None) -> List[List[str]]:
    condition = f' WHERE teacher_id = {teacher_id}' if teacher_id else ''
    request = f"SELECT students.name, score FROM students INNER JOIN teachers ON teacher_id == teachers.id{condition} ORDER BY score DESC LIMIT 10"
    cursor.execute(request)
    records = cursor.fetchall()
    return records


# Edit main message
async def main_edit_mes(text: str, ikb: InlineKeyboardMarkup, call=None, message_id: int = None, chat_id: int = None) -> None:
    if chat_id == None and message_id == None and call != None:
        message_id = call.message.message_id
        chat_id = call.message.chat.id
    try:
        await bot.edit_message_text(
            text=text,
            message_id=message_id,
            chat_id=chat_id,
            reply_markup=ikb,
            parse_mode='html')
    except MessageNotModified:
        pass


if __name__ == "__main__":
    print(get_top_std(1))
