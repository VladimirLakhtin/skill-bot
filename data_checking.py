from typing import List, Any
import datetime


def cheak_input_text(name, key):
        layout = dict(zip(map(ord, "qwertyuiop[]asdfghjkl;'zxcvbnm,./`"
                                   'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>?~'),
                          "йцукенгшщзхъфывапролджэячсмитьбю.ё"
                          'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё'))
        text_edit = name.translate(layout)
        with open("ASCII.txt") as f:
            for i in f:
                sym = i.split()
        list_exept_sym = []
        for index_sym_in_name in text_edit:
            if index_sym_in_name in sym:
                list_exept_sym.append(index_sym_in_name)
        if name == text_edit and len(list_exept_sym) == 0:
            return text_edit, "ok", name
        elif len(list_exept_sym) == 0:
            text = f"Возможно вы имели ввиду {key}: {name.translate(layout)}"
            return text, "normal", text_edit
        else:
            list_exept_sym = "|".join(list_exept_sym)
            text = f"В {key} не должены стоять символы: {list_exept_sym}"
            return text, "bad"


def input_edit(inputs: Any, column: str) -> (bool, str):
    if column in ["reward", "cost", "score"]:
        flag = inputs.isdigit() and int(inputs) >= 0
        text = "Число должно быть <b>положительным</b>" if not flag else ""
    elif column == "name":
        flag = len(inputs.split()) == 2
        text = "Необходимо ввести <b>имя и фамилию</b>" if not flag else ""
    elif column == 'date':
        flag = (len(inputs) == 10) and \
                 ([int(len(i)) for i in inputs.split('.')] == [2, 2, 4]) and \
                 (sum([i.isdigit() for i in inputs.split('.')]) == 3)
        text = "Необходимо ввести дату в формате <b>ДЕНЬ.МЕСЯЦ.ГОД</b>" if not flag else ""
    else:
        return True, None
    return flag, text


def input_data(text_data):
    flag = text_data.isdigit() and int(text_data) <= 30 and int(text_data) > 0
    if flag:
        now = datetime.datetime.now()
        if int(text_data) < 10 and int(now.month) < 10:
            return flag, f"{now.year}-0{now.month}-0{text_data}"
        else:
            return flag, f"{now.year}-{now.month}-{text_data}"
    else:
        if not(text_data.isdigit()):
            text = "Введите <b>именно число</b>"
        elif int(text_data) > 31:
            text = "Такого дня в месяце нет"
        else:
            text = "Число должно быть положительным"
        return flag, text

