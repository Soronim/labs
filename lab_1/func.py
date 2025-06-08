from validate import get_valid_input, validate_date, validate_login, validate_name, validate_password,capitalize_name
import print_user as pu
from datetime import datetime
import psycopg2
import re
from typing import List, Optional


def user_retrieve_all(conn):
    """Получает список всех пользователей из базы данных"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.id, u.login, u.registration_date, 
                       a.family, a.name, a.patronymic, a.birth_date,
                       array_agg(t.title) as tags
                FROM users u
                JOIN accounts a ON u.id = a.user_id
                LEFT JOIN unnest(a.tags) as tag_id ON true
                LEFT JOIN tags t ON t.id = tag_id
                GROUP BY u.id, a.family, a.name, a.patronymic, a.birth_date
                ORDER BY u.registration_date DESC
            """)
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении списка пользователей: {e}")
        return None

def register_user(conn, login, password, family, name, patronymic, birth_date):
    try:
        with conn.cursor() as cursor:
            # Вызывов процедурки
            cursor.execute(
                "CALL register_user(%s, %s, %s, %s, %s, %s, %s)",
                (login, password, family, name, patronymic, birth_date, None)
            )
            # Получаем OUT значением
            cursor.execute("SELECT %s", (cursor.fetchone()[0],))
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
            
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
        

def create_tag(conn, title: str) -> Optional[int]:
    """Создает новый тег и возвращает его ID"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tags (title) VALUES (%s) RETURNING id",
                (title,)
            )
            tag_id = cursor.fetchone()[0]
            conn.commit()
            return tag_id
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при создании тега: {e}")
        return None

def add_tag_to_account(conn, user_id: int, tag_id: int) -> bool:
    """Добавляет тег к аккаунту пользователя (если его еще нет)"""
    try:
        with conn.cursor() as cursor:
            # Проверяем, есть ли уже такой тег у пользователя
            cursor.execute("""
                SELECT 1 FROM accounts 
                WHERE user_id = %s AND %s = ANY(tags)
                """, (user_id, tag_id))
            if cursor.fetchone():
                print("У пользователя уже есть этот тег")
                return False
                
            cursor.callproc('add_tag_to_account', (user_id, tag_id))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении тега к пользователю: {e}")
        return False

def remove_tag_from_account(conn, user_id: int, tag_id: int) -> bool:
    """Удаляет тег из аккаунта пользователя"""
    try:
        with conn.cursor() as cursor:
            cursor.callproc('remove_tag_from_account', (user_id, tag_id))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при удалении тега у пользователя: {e}")
        return False

def delete_tag(conn, tag_id: int) -> bool:
    """Удаляет тег из системы"""
    try:
        with conn.cursor() as cursor:
            cursor.callproc('delete_tag', (tag_id,))
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при удалении тега: {e}")
        return False

def get_all_tags(conn) -> Optional[List[dict]]:
    """Возвращает все существующие теги, отсортированные по ID"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title FROM tags ORDER BY id")
            return [{'id': row[0], 'title': row[1]} for row in cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении списка тегов: {e}")
        return None


def get_account_tags(conn, user_id: int) -> Optional[List[dict]]:
    """Возвращает все теги аккаунта, отсортированные по ID"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.id, t.title 
                FROM accounts a, unnest(a.tags) AS tag_id
                JOIN tags t ON t.id = tag_id
                WHERE a.user_id = %s
                ORDER BY t.id
            """, (user_id,))
            return [{'id': row[0], 'title': row[1]} for row in cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении тегов пользователя: {e}")
        return None

def show_tag_menu(conn):
    """Меню для работы с тегами"""
    tag_menu = '''
Управление тегами:
1. Показать все теги
2. Добавить теги пользователю
3. Удалить теги у пользователя
4. Создать новый тег
5. Удалить тег из системы
6. Показать теги пользователя
=============================
0. Назад
'''
    while True:
        print(tag_menu)
        operation = input('ВЫБОР: ').strip()
        
        match operation:
            case '0':
                break
                
            case '1':
                tags = get_all_tags(conn)
                if tags:
                    print("\nСписок всех тегов:")
                    for tag in tags:
                        print(f"{tag['id']}: {tag['title']}")
                else:
                    print("\nТеги не найдены")
                    
            case '2':
                while True:
                    user_id = input("\nID пользователя (или 'отмена' для возврата): ").strip()
                    if user_id.lower() == 'отмена':
                        break
                        
                    if not user_id.isdigit():
                        print("Ошибка: ID пользователя должен быть числом")
                        continue
                        
                    if not check_user_exists(conn, int(user_id)):
                        print("Ошибка: пользователь с таким ID не найден")
                        continue
                        
                    tags = get_all_tags(conn)
                    if not tags:
                        print("Нет доступных тегов для добавления")
                        break
                        
                    print("\nДоступные теги (ID: Название):")
                    for tag in sorted(tags, key=lambda x: x['id']):
                        print(f"{tag['id']}: {tag['title']}")
                        
                    tag_input = input("\nВведите ID тегов для добавления (через запятую или пробел): ").strip()
                    if not tag_input:
                        print("Не указаны теги для добавления")
                        continue
                        
                    added_count = 0
                    existing_tags = {tag['id'] for tag in (get_account_tags(conn, int(user_id)) or [])}
                    
                    for part in re.split(r'[, \s]+', tag_input):
                        if not part.isdigit():
                            continue
                            
                        tag_id = int(part)
                        
                        if not any(tag['id'] == tag_id for tag in tags):
                            continue
                            
                        if tag_id in existing_tags:
                            continue
                            
                        if add_tag_to_account(conn, int(user_id), tag_id):
                            added_count += 1
                            existing_tags.add(tag_id)
                    
                    print(f"\nУспешно добавлено тегов: {added_count}")
                    break
                    
            case '3':  # Обновлённый вариант удаления тегов
                while True:
                    user_id = input("\nID пользователя (или 'отмена' для возврата): ").strip()
                    if user_id.lower() == 'отмена':
                        break
                        
                    if not user_id.isdigit():
                        print("Ошибка: ID пользователя должен быть числом")
                        continue
                        
                    user_tags = get_account_tags(conn, int(user_id))
                    if not user_tags:
                        print("У пользователя нет тегов или пользователь не найден")
                        continue
                        
                    print("\nТекущие теги пользователя:")
                    for tag in sorted(user_tags, key=lambda x: x['id']):
                        print(f"{tag['id']}: {tag['title']}")
                        
                    tag_input = input("\nВведите ID тегов для удаления (через запятую или пробел): ").strip()
                    if not tag_input:
                        print("Не указаны теги для удаления")
                        continue
                        
                    removed_count = 0
                    user_tag_ids = {tag['id'] for tag in user_tags}
                    
                    for part in re.split(r'[, \s]+', tag_input):
                        if not part.isdigit():
                            continue
                            
                        tag_id = int(part)
                        
                        if tag_id not in user_tag_ids:
                            continue
                            
                        if remove_tag_from_account(conn, int(user_id), tag_id):
                            removed_count += 1
                            user_tag_ids.remove(tag_id)
                    
                    print(f"\nУспешно удалено тегов: {removed_count}")
                    break
                    
            case '4':
                while True:
                    title = input("\nНазвание нового тега (или 'отмена' для возврата): ").strip()
                    if title.lower() == 'отмена':
                        break
                        
                    if not title:
                        print("Ошибка: название тега не может быть пустым")
                        continue
                        
                    tag_id = create_tag(conn, title)
                    if tag_id:
                        print(f"Тег создан с ID: {tag_id}")
                    break
                    
            case '5':
                while True:
                    tags = get_all_tags(conn)
                    if not tags:
                        print("Нет тегов для удаления")
                        break
                        
                    print("\nДоступные теги:")
                    for tag in sorted(tags, key=lambda x: x['id']):
                        print(f"{tag['id']}: {tag['title']}")
                        
                    tag_id = input("\nВведите ID тега для удаления (или 'отмена'): ").strip()
                    if tag_id.lower() == 'отмена':
                        break
                        
                    if not tag_id.isdigit():
                        print("Ошибка: ID тега должен быть числом")
                        continue
                        
                    tag_id = int(tag_id)
                    if not any(tag['id'] == tag_id for tag in tags):
                        print("Тег с таким ID не существует")
                        continue
                        
                    confirm = input(f"Вы уверены, что хотите удалить тег ID {tag_id}? (да/нет): ").strip().lower()
                    if confirm == 'да':
                        if delete_tag(conn, tag_id):
                            print("Тег успешно удален")
                    break
                    
            case '6':
                while True:
                    user_id = input("\nID пользователя (или 'отмена' для возврата): ").strip()
                    if user_id.lower() == 'отмена':
                        break
                        
                    if not user_id.isdigit():
                        print("Ошибка: ID пользователя должен быть числом")
                        continue
                        
                    tags = get_account_tags(conn, int(user_id))
                    if tags:
                        print(f"\nТеги пользователя {user_id}:")
                        for tag in sorted(tags, key=lambda x: x['id']):
                            print(f"- {tag['title']} (ID: {tag['id']})")
                    else:
                        print("У пользователя нет тегов или пользователь не найден")
                    break
                    
            case _:
                print('\nНеверная команда')


def check_user_exists(conn, user_id):
    """Проверяет, существует ли пользователь с указанным ID"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False