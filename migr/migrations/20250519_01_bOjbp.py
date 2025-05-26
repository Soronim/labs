from yoyo import step

steps = [
    
step(
    """
    CREATE OR REPLACE PROCEDURE register_user(
    p_login VARCHAR(32),
    p_password VARCHAR(128),
    p_family VARCHAR(64),
    p_name VARCHAR(64),
    p_patronymic VARCHAR(64),
    p_birth_date DATE,
    INOUT user_id INTEGER DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Вставка в таблицу users
    INSERT INTO users (login, password)
    VALUES (p_login, p_password)
    RETURNING id INTO user_id;
    
    -- Вставка в таблицу accounts
    INSERT INTO accounts (user_id, family, name, patronymic, birth_date)
    VALUES (user_id, p_family, p_name, p_patronymic, p_birth_date);
    
EXCEPTION WHEN OTHERS THEN
    RAISE EXCEPTION 'Registration failed: %', SQLERRM;
END;
$$;
    """,
    "DROP PROCEDURE IF EXISTS register_user(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, DATE, OUT INTEGER)"
)
]