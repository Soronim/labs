def register_user(conn, login, password, family, name, patronymic, birth_date):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT register_user(%s, %s, %s, %s, %s, %s)",
                (login, password, family, name, patronymic, birth_date)
            )
            user_id = cursor.fetchone()[0]
            conn.commit()
            return user_id
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при регистрации пользователя: {e}")
        return None