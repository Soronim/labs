import print_user as pu
from datetime import datetime
import psycopg2
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
    """Проверяет корректность логина и его уникальность в базе данных (регистронезависимо)"""
    if not login:
        print('Ошибка: логин не может быть пустым')
        return False
    
    if len(login) < 4:
        print('Ошибка: логин должен содержать минимум 4 символа')
        return False
    
    if len(login) > 32:
        print('Ошибка: логин должен содержать максимум 32 символа')
        return False
    
    if not re.match(r'^[a-zA-Z0-9_]+$', login):
        print('Ошибка: логин может содержать только латинские буквы, цифры и подчеркивание')
        return False
    
    # Проверка уникальности логина (регистронезависимая), если передан connection
    if conn:
        try:
            with conn.cursor() as cursor:
                # Сравниваем lowercase версии логинов
                cursor.execute("SELECT id FROM users WHERE LOWER(login) = LOWER(%s)", (login,))
                if cursor.fetchone():
                    print('Ошибка: этот логин уже занят (учтите, что проверка не чувствительна к регистру)')
                    return False
        except Exception as e:
            print(f'Ошибка при проверке уникальности логина: {e}')
            return False
    
    return True


def validate_password(password: str) -> bool:
    """Проверяет сложность пароля и выводит все ошибки сразу"""
    errors = []
    
    if not password:
        errors.append('пароль не может быть пустым')
    
    if len(password) < 8:
        errors.append('пароль должен содержать минимум 8 символов')
    
    if not re.search(r'[A-Z]', password):
        errors.append('пароль должен содержать хотя бы одну заглавную букву')
    
    if not re.search(r'[a-z]', password):
        errors.append('пароль должен содержать хотя бы одну строчную букву')
    
    if not re.search(r'[0-9]', password):
        errors.append('пароль должен содержать хотя бы одну цифру')
    
    if not re.search(r'[^A-Za-z0-9]', password):
        errors.append('пароль должен содержать хотя бы один специальный символ')
    
    if errors:
        print('Ошибки в пароле:')
        for error in errors:
            print(f'- {error}')
        return False
    
    return True

def validate_date(date_str: str) -> bool:
    """Проверяет корректность даты и что возраст пользователя не менее 14 лет"""
    try:
        # Сначала проверяем формат даты
        birth_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        
        if birth_date > today:
            print('Ошибка: дата рождения не может быть в будущем')
            return False
            
        # Вычисляем возраст
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 14:
            print('Ошибка: для регистрации пользователь должен быть не младше 14 лет')
            return False
        
        return True
    except ValueError as e:
        # Проверяем, связано ли исключение с несуществующей датой
        if "day is out of range for month" in str(e) or "month must be in 1..12" in str(e):
            print('Ошибка: введена некорректная дата (несуществующий день или месяц)')
        else:
            print('Ошибка: Неверный формат даты. Используйте ГГГГ-ММ-ДД')
        return False
    
def get_valid_input(prompt: str, validator: callable, *args, **kwargs) -> str:
    """Получает валидный ввод от пользователя с немедленной проверкой"""
    while True:
        value = input(prompt).strip()
        if validator(value, *args, **kwargs):
            return value
        