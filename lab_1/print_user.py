from datetime import datetime

def print_users(users):
    if not users:
        print("Нет пользователей для отображения")
        return
    
    # Определяем заголовки столбцов
    headers = [
        ("ID", 'id'),
        ("Логин", 'login'),
        ("Дата регистрации", 'reg_date'),
        ("Фамилия", 'family'),
        ("Имя", 'name'),
        ("Отчество", 'patronymic'),
        ("Дата рождения", 'birth_date')
    ]
    
    # Преобразуем данные пользователей в удобный формат
    formatted_users = []
    for user in users:
        reg_date = user[2].strftime("%Y-%m-%d %H:%M:%S") if isinstance(user[2], datetime) else str(user[2])
        birth_date = user[6].strftime("%Y-%m-%d") if isinstance(user[6], datetime) else str(user[6])
        
        formatted_users.append({
            'id': str(user[0]),
            'login': str(user[1]),
            'reg_date': reg_date,
            'family': str(user[3]),
            'name': str(user[4]),
            'patronymic': str(user[5]) if user[5] else '-',
            'birth_date': birth_date
        })
    
    # Вычисляем максимальную ширину для каждого столбца
    col_widths = {}
    for header, key in headers:
        # Начинаем с ширины заголовка
        max_width = len(header)
        # Проверяем все данные пользователей для этого столбца
        for user in formatted_users:
            if len(user[key]) > max_width:
                max_width = len(user[key])
        # Добавляем небольшой отступ
        col_widths[key] = max_width + 2
    
    # Строим строку формата для вывода
    header_parts = []
    for header, key in headers:
        header_parts.append(f"{header:<{col_widths[key]}}")
    header_line = " | ".join(header_parts)
    
    separator = '-' * len(header_line)
    
    print("\nСписок пользователей:")
    print(separator)
    print(header_line)
    print(separator)
    
    for user in formatted_users:
        user_parts = []
        for _, key in headers:
            user_parts.append(f"{user[key]:<{col_widths[key]}}")
        user_line = " | ".join(user_parts)
        print(user_line)
    
    print(separator)