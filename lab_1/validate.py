import print_user as pu
import psycopg2
import re

def capitalize_name(name):
    """Приводит имя к виду с заглавной первой буквой, остальные - строчные"""
    if not name:
        return name
    return name[0].upper() + name[1:].lower()

def validate_name(name: str, field_name: str, is_required: bool = True) -> bool:
    if not name:
        if is_required:
            print(f'Ошибка: поле {field_name} не может быть пустым')
            return False
        return True
    
    # Изменено: разрешаем только апостроф ’ (U+2019) и запрещаем прямой апостроф '
    if not re.match(r'^[А-Яа-яЁё’"\u2018\u2019\u201B\u2032\u2035\s\-.,()]+$', name):
        print(f'Ошибка: поле {field_name} содержит недопустимые символы. '
              f'Допустимы только русские буквы, апострофы (’), дефисы, пробелы, точки, запятые и скобки')
        return False
    
    # Проверка что есть хотя бы одна буква (не только спецсимволы)
    if not re.search(r'[А-Яа-яЁё]', name):
        print(f'Ошибка: поле {field_name} должно содержать хотя бы одну букву')
        return False
    
    # Проверка на двойные пробелы и другие повторяющиеся спецсимволы
    if re.search(r'([.\-’ ,()])\1', name):  # Убрал прямой апостроф из проверки
        print(f'Ошибка: поле {field_name} содержит повторяющиеся специальные символы подряд')
        return False
    
    # Проверка на недопустимые комбинации спецсимволов
    if re.search(r'[.\-’,()]{2,}', name):  # Убрал прямой апостроф из проверки
        print(f'Ошибка: поле {field_name} содержит недопустимые сочетания специальных символов')
        return False
    
    # Проверки для фамилии
    if field_name.lower() == 'фамилия':
        if name[0] in ('.', '-', '’', ' ', ',', ')'):  # Заменил прямой апостроф на ’
            print(f'Ошибка: фамилия не может начинаться с символа "{name[0]}"')
            return False
        if name[-1] in ('.', '-', '’', ' ', ',', '('):  # Заменил прямой апостроф на ’
            print(f'Ошибка: фамилия не может заканчиваться символом "{name[-1]}"')
            return False
        if len(name) == 1 and name in ('.', '-', '’', ' ', ',', '(', ')'):  # Заменил прямой апостроф на ’
            print(f'Ошибка: фамилия не может состоять только из символа "{name}"')
            return False
    
    # Проверки для имени и отчества
    if field_name.lower() in ('имя', 'отчество'):
        if name[0] in ('-', '’', ' ', ',', '.', ')'):  # Заменил прямой апостроф на ’
            print(f'Ошибка: {field_name} не может начинаться с символа "{name[0]}"')
            return False
        if name[-1] in ('-', '’', ' ', ',', '('):  # Заменил прямой апостроф на ’
            print(f'Ошибка: {field_name} не может заканчиваться символом "{name[-1]}"')
            return False
        if len(name) == 1 and name in ('-', '’', ' ', ',', '.', '(', ')'):  # Заменил прямой апостроф на ’
            print(f'Ошибка: {field_name} не может состоять только из символа "{name}"')
            return False
    
    
    if '(' in name or ')' in name:
        stack = []
        for i, char in enumerate(name):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if not stack:
                    print(f'Ошибка: поле {field_name} содержит непраные скобки')
                    return False
                stack.pop()
                
    # Проверка на непарные скобки
    if name.count('(') != name.count(')'):
        print(f'Ошибка: поле {field_name} содержит непарные скобки')
        return False
    
    # Проверка на латинские буквы I, V
    if re.search(r'[IViv]', name):
        print(f'Ошибка: поле {field_name} содержит недопустимые латинские буквы (I, V)')
        return False
    if name[0].upper() in ('I', 'V'):
        print(f'Ошибка: поле {field_name} не может начинаться с латинской буквы {name[0].upper()}')
        return False
    
    return True

def validate_email(email: str) -> bool:
    """Проверяет корректность email согласно требованиям БД"""
    if not email:
        print('Ошибка: email не может быть пустым')
        return False
    
    email = email.strip()
    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', email, re.IGNORECASE):
        print('Ошибка: некорректный формат email')
        return False
    
    return True

def validate_password(password: str) -> bool:
    """Проверяет сложность пароля согласно требованиям БД"""
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
