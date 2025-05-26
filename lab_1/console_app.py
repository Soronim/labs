from connection import get_db_connection
import print_user as pu
from datetime import datetime
import psycopg2
from func import register_user_interactive, show_all_users
import re




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