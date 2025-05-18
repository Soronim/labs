from yoyo import step

steps = [
    step(
        """
        CREATE OR REPLACE FUNCTION register_user(
            p_login VARCHAR(150),
            p_password VARCHAR(128),
            p_family VARCHAR(150),
            p_name VARCHAR(150),
            p_patronymic VARCHAR(150),
            p_birth_date DATE
        ) RETURNS INTEGER AS $$
        DECLARE
            user_id INTEGER;
        BEGIN
            -- Начало транзакции
            BEGIN
                -- Вставляем данные в таблицу users
                INSERT INTO users (login, password)
                VALUES (p_login, p_password)
                RETURNING id INTO user_id;
                
                -- Вставляем данные в таблицу accounts
                INSERT INTO accounts (user_id, family, name, patronymic, birth_date)
                VALUES (user_id, p_family, p_name, p_patronymic, p_birth_date);
                
                -- Если все успешно, возвращаем ID пользователя
                RETURN user_id;
                
            EXCEPTION
                WHEN OTHERS THEN
                    -- В случае ошибки откатываем транзакцию
                    RAISE EXCEPTION 'Error during registration: %', SQLERRM;
                    RETURN NULL;
            END;
        END;
        $$ LANGUAGE plpgsql;
        """,
        "DROP FUNCTION IF EXISTS register_user(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, DATE)"
    )
]