#Проверка данных имени на ввод
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

def input_edit(inputs, column):
    if column in ["reward", "cost", "score"]:
        flag = inputs.isdigit() and int(inputs) >= 0
        if not flag:
            text = 'Введите именно положительное число'
        else:
            text = ""
        return flag, text
    elif column == "name":
        flag = len(inputs.split()) == 2
        if not flag:
            text = "Введите имя и фамилию"
        else:
            text = ""
        return flag, text
    return True, None
