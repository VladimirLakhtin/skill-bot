import sqlite3


connection = sqlite3.connect("db_Skill_Box_main.db")
cursor = connection.cursor()


def db(name_bd):
    cursor.execute(f"""SELECT * from {name_bd}""")
    records = cursor.fetchall()
    return sorted(records)


def name_list_db_student_and_teacher(key):
        records = db("Skill_Box")
        list_name = []
        list_id = []
        if key == "student":
            class_human = "Студент"
        else:
            class_human = "Куратор"
        for i in records:
            if i[-1] == class_human:
                list_name.append(i[1])
                list_id.append(i[0])
        return list_name, list_id


def info_list(call, key):
    id_student = name_list_db_student_and_teacher(key=key)[1]
    index_id = id_student[int(call) - 1]
    cursor.execute("""select * from Skill_Box where id = ?""", (index_id, ))
    info = cursor.fetchall()
    list_info = [str(i) for i in info[0]]
    text_info = f"ID - {list_info[0]}\nИмя - {list_info[1]}\nПрофессия - {list_info[2]}\nТГ-id - {list_info[3]}\nSkillCoins - {list_info[4]}\nАртикул профессии - {list_info[5]}\n"
    return text_info, list_info[0]


def removing_student(call_text):
    id = call_text
    cursor.execute("""DELETE from "Skill_Box" where id = ?""", (id, ))
    connection.commit()

def add_type(name_type):
    cursor.execute("""INSERT INTO Type_and_articul (Type) VALUES (?)""", ([name_type]))
    connection.commit()


def add_student(name, type, id_tg, articul, class_human):
    cursor.execute("INSERT INTO Skill_Box (Name, Type, ID_Tg, Rating, Articul, Class) VALUES (?, ?, ?, ?, ?, ?)", ([name, type, id_tg, 0, articul, class_human]))
    connection.commit()