from connection import get_db_connection
import print_user as pu
from datetime import datetime
import psycopg2
from procedures import register_user
import re

def capitalize_name(name):
    """Приводит имя к виду с заглавной первой буквой, остальные - строчные"""
    if not name:
        return name
    return name[0].upper() + name[1:].lower()

def validate_name(name: str, field_name: str, is_required: bool = True) -> bool:
    """Валидация имени, фамилии или отчества"""
    if not name:
        if is_required:
            print(f'Ошибка: поле {field_name} не может быть пустым')
            return False
        return True
    
    if not re.match(r'^[А-Яа-яЁё’"\u2018\u2019\u201B\u2032\u2035\s\-.,()]+$', name):
        print(f'Ошибка: поле {field_name} содержит недопустимые символы. '
              f'Допустимы только русские буквы, апострофы (’), дефисы, пробелы, точки, запятые и скобки')
        return False
    
    if not re.search(r'[А-Яа-яЁё]', name):
        print(f'Ошибка: поле {field_name} должно содержать хотя бы одну букву')
        return False
    
    if re.search(r'([.\-’ ,()])\1', name):
        print(f'Ошибка: поле {field_name} содержит повторяющиеся специальные символы подряд')
        return False
    
    if re.search(r'[.\-’,()]{2,}', name):
        print(f'Ошибка: поле {field_name} содержит недопустимые сочетания специальных символов')
        return False
    
    if field_name.lower() == 'фамилия':
        if name[0] in ('.', '-', '’', ' ', ',', ')'):
            print(f'Ошибка: фамилия не может начинаться с символа "{name[0]}"')
            return False
        if name[-1] in ('.', '-', '’', ' ', ',', '('):
            print(f'Ошибка: фамилия не может заканчиваться символом "{name[-1]}"')
            return False
    
    if field_name.lower() in ('имя', 'отчество'):
        if name[0] in ('-', '’', ' ', ',', '.', ')'):
            print(f'Ошибка: {field_name} не может начинаться с символа "{name[0]}"')
            return False
        if name[-1] in ('-', '’', ' ', ',', '('):
            print(f'Ошибка: {field_name} не может заканчиваться символом "{name[-1]}"')
            return False
    
    if '(' in name or ')' in name:
        if name.count('(') != name.count(')'):
            print(f'Ошибка: поле {field_name} содержит непарные скобки')
            return False
    
    if re.search(r'[IViv]', name):
        print(f'Ошибка: поле {field_name} содержит недопустимые латинские буквы (I, V)')
        return False
    
    return True


def validate_login(login: str, conn=None) -> bool:
    """Проверяет корректность логина и его уникальность в базе данных"""
    if not login:
        print('Ошибка: логин не может быть пустым')
        return False
    
    if len(login) < 4:
        print('Ошибка: логин должен содержать минимум 4 символа')
        return False
    
    if not re.match(r'^[a-zA-Z0-9_]+$', login):
        print('Ошибка: логин может содержать только латинские буквы, цифры и подчеркивание')
        return False
    
    # Проверка уникальности логина, если передан connection
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE login = %s", (login,))
                if cursor.fetchone():
                    print('Ошибка: этот логин уже занят')
                    return False
        except Exception as e:
            print(f'Ошибка при проверке уникальности логина: {e}')
            return False
    
    return True


def validate_password(password: str) -> bool:
    """Проверяет сложность пароля"""
    if not password:
        print('Ошибка: пароль не может быть пустым')
        return False
    
    if len(password) < 8:
        print('Ошибка: пароль должен содержать минимум 8 символов')
        return False
    
    if not re.search(r'[A-Z]', password):
        print('Ошибка: пароль должен содержать хотя бы одну заглавную букву')
        return False
    
    if not re.search(r'[a-z]', password):
        print('Ошибка: пароль должен содержать хотя бы одну строчную букву')
        return False
    
    if not re.search(r'[0-9]', password):
        print('Ошибка: пароль должен содержать хотя бы одну цифру')
        return False
    
    if not re.search(r'[^A-Za-z0-9]', password):
        print('Ошибка: пароль должен содержать хотя бы один специальный символ')
        return False
    
    return True

def validate_date(date_str: str) -> bool:
    """Проверяет корректность даты"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        if date > datetime.now().date():
            print('Ошибка: дата не может быть в будущем')
            return False
        return True
    except ValueError:
        print('Ошибка: Неверный формат даты. Используйте ГГГГ-ММ-ДД')
        return False

def get_valid_input(prompt: str, validator: callable, *args, **kwargs) -> str:
    """Получает валидный ввод от пользователя с немедленной проверкой"""
    while True:
        value = input(prompt).strip()
        if validator(value, *args, **kwargs):
            return value

def user_retrieve_all(conn):
    """Получает список всех пользователей из базы данных"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.login, u.registration_date, 
                       a.family, a.name, a.patronymic, a.birth_date
                FROM users u
                JOIN accounts a ON u.id = a.user_id
                ORDER BY u.registration_date DESC
            """)
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении списка пользователей: {e}")
        return None

def register_user_interactive(conn):
    """Интерактивный процесс регистрации пользователя"""
    print('\nРегистрация нового пользователя:')
    
    login = get_valid_input('Логин: ', validate_login, conn)  # Передаем соединение как аргумент
    password = get_valid_input('Пароль: ', validate_password)
    family = get_valid_input('Фамилия: ', validate_name, "фамилия")
    name = get_valid_input('Имя: ', validate_name, "имя")
    patronymic = get_valid_input('Отчество (необязательно): ', validate_name, "отчество", False) or None
    birth_date = get_valid_input('Дата рождения (ГГГГ-ММ-ДД): ', validate_date)
    
    try:
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        user_id = register_user(
            conn, 
            login, 
            password, 
            capitalize_name(family), 
            capitalize_name(name), 
            capitalize_name(patronymic) if patronymic else None, 
            birth_date
        )
        
        if user_id:
            print(f'\nПользователь успешно зарегистрирован с ID: {user_id}')
        else:
            print('\nНе удалось зарегистрировать пользователя')
    except Exception as e:
        print(f'\nОшибка при регистрации пользователя: {e}')

def show_all_users(conn):
    """Отображает список всех пользователей"""
    users = user_retrieve_all(conn)
    if users:
        pu.print_users(users)
    else:
        print('\nВ базе нет пользователей')

menu = '''
Выберите операцию:
1. Зарегистрировать пользователя
2. Показать всех пользователей
=============================
0. Выйти
'''

def main():
    """Основная функция приложения"""
    conn = get_db_connection()
    
    try:
        while True:
            print(menu)
            operation = input('ВЫБОР: ').strip()
            
            match operation:
                case '0':
                    print('Выход из приложения.')
                    break

                case '1':
                    register_user_interactive(conn)

                case '2':
                    show_all_users(conn)

                case _:
                    print('\nНеверная команда')
    finally:
        conn.close()

if __name__ == "__main__":
    main()