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
            OUT user_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO users (login, password)
            VALUES (p_login, p_password)
            RETURNING id INTO user_id;
            
            INSERT INTO accounts (user_id, family, name, patronymic, birth_date)
            VALUES (user_id, p_family, p_name, p_patronymic, p_birth_date);
        END;
        $$;
        """,
        "DROP PROCEDURE IF EXISTS register_user(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, DATE)"
    )
]
#Почитать про хранмые процедуры 
#Может ли INOUT user_id если явно указать user_id создать пользователя с этим id