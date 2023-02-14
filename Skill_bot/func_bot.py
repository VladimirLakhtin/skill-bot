import sqlite3
import difflib

#Конект с БД
connection = sqlite3.connect("db_Skill_Box_main.db")
cursor = connection.cursor()

#Список данных из бд
def db(name_bd):
    cursor.execute(f"""SELECT * from {name_bd}""")
    records = cursor.fetchall()
    return sorted(records)


#Берём данные id и имени из бд по типу студент или куратор: 
def name_list_db_student_and_teacher(key):
        records = db("Skill_Box")
        list_name = []
        list_id = []
        class_human = "Студент" if key == "student" else "Куратор"
        for i in records:
            if i[-1] == class_human:
                list_name.append(i[1])
                list_id.append(i[0])
        return list_name, list_id

#Возвращаем список поиска студентов или кураторов при помощи вероятности совпадения букв в фамилии и в имени
#TODO: Доработать
def search_db_student_teacher(key, name):
    lsit_name_search_human_probability = []
    list_name_search_human_100_probability = []
    try:
        list_name = name_list_db_student_and_teacher(key)[0]
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




#Берём информацию по студенту или куратору по id кнопки
def info_list(call, key):
    id_human = name_list_db_student_and_teacher(key=key)[1]
    index_id = id_human[int(call) - 1]
    cursor.execute("""select * from Skill_Box where id = ?""", (index_id, ))
    info = cursor.fetchall()
    list_info = [str(i) for i in info[0]]
    text_info = f"ID - {list_info[0]}\nИмя - {list_info[1]}\nПрофессия - {list_info[2]}\nТГ-id - {list_info[3]}\nSkillCoins - {list_info[4]}\nАртикул профессии - {list_info[5]}\n"
    return text_info, list_info[0]


#Удаляем человека из бд по id
#TODO: Переименуй функцию и в хендлере тоже пж
def removing_student(call_text):
    id = call_text
    cursor.execute("""DELETE from "Skill_Box" where id = ?""", (id, ))
    connection.commit()

#Добавляем тип профессии
#TODO: Можешь тоже переименовать если хочешь
def add_type(name_type):
    name_type = name_type.split()
    name_type = " ".join(name_type)
    cursor.execute("""INSERT INTO Type_and_articul (Type) VALUES (?)""", ([name_type]))
    connection.commit()

#Добавляем человека в бд
#TODO: Переименуй функцию и в хендлере тоже пж
def add_student(name, type, id_tg, articul, class_human):
    name = name.split()
    name = " ".join(name)
    id_tg = id_tg.split()
    id_tg = " ".join(id_tg)
    cursor.execute("INSERT INTO Skill_Box (Name, Type, ID_Tg, Rating, Articul, Class) VALUES (?, ?, ?, ?, ?, ?)", ([name, type, id_tg, 0, articul, class_human]))
    connection.commit()

