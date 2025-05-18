from prettytable import PrettyTable, ALL
from textwrap import fill

def print_users(users_data: list) -> None:
    """Выводит список пользователей в виде форматированной таблицы
    
    Args:
        users_data: Список кортежей с данными пользователей в формате:
                   (user_id, login, password, family, name, patronymic, birth_date, born_date)
    """
    table = PrettyTable()
    table.hrules = ALL
    table.field_names = [
        '№', 
        'ID', 
        'Логин', 
        'Пароль', 
        'Фамилия', 
        'Имя',
        'Отчество',
        'Дата Рождения',
        'Дата Создания Аккаунта'
    ]
    table.align = 'l'
    table.max_width = 20  # Максимальная ширина колонки
    table.sortby = '№'
    
    for i, user in enumerate(users_data, 1):
        table.add_row([
            i,
            user[0],  # user_id
            fill(user[2] if user[2] else '', width=15),  # last_name
            fill(user[1] if user[1] else '', width=15),  # first_name
            fill(user[3] if user[3] else '-', width=15),  # middle_name
            fill(user[4], width=25),  # email
            fill(user[5], width=15)  # password 
        ], divider=True)
    
    print(table.get_string())