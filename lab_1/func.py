from validate import get_valid_input, validate_date, validate_login, validate_name, validate_password,capitalize_name
import print_user as pu
from datetime import datetime
import psycopg2
import re



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

def register_user(conn, login, password, family, name, patronymic, birth_date):
    try:
        with conn.cursor() as cursor:
            # Вызываем процедуру регистрации
            cursor.execute(
                "CALL register_user(%s, %s, %s, %s, %s, %s, NULL)",
                (login, password, family, name, patronymic, birth_date)
            )
            
            # Получаем ID только что созданного пользователя
            cursor.execute("SELECT id FROM users WHERE login = %s", (login,))
            user_id = cursor.fetchone()[0]
            
            conn.commit()
            return user_id  # Возвращаем ID пользователя
            
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при регистрации пользователя: {e}")
        return None

def register_user_interactive(conn):
    print('\nРегистрация нового пользователя:')
    
    login = get_valid_input('Логин: ', validate_login, conn) 
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