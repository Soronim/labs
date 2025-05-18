"""

"""

from yoyo import step

__depends__ = {'20250518_01_LIiPW'}

steps = [
    step("""
         CREATE TABLE accounts (
             user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    family VARCHAR(150) NOT NULL
        CHECK (family ~ '^[А-Яа-яЁё''’()\s-]+$')
        CONSTRAINT no_double_spaces_family CHECK (family !~ '\s{2}')
        CONSTRAINT no_leading_trailing_spaces_family CHECK (family = trim(family)),
    name VARCHAR(150) NOT NULL
        CHECK (name ~ '^[А-Яа-яЁё''’()\s-]+$')
        CONSTRAINT no_double_spaces_name CHECK (name !~ '\s{2}')
        CONSTRAINT no_leading_trailing_spaces_name CHECK (name = trim(name)),
    patronymic VARCHAR(150)
        CHECK (patronymic ~ '^[А-Яа-яЁё''’()\s-]+$' OR patronymic IS NULL)
        CONSTRAINT no_double_spaces_patronymic CHECK (patronymic !~ '\s{2}' OR patronymic IS NULL)
        CONSTRAINT no_leading_trailing_spaces_patronymic CHECK (patronymic = trim(patronymic) OR patronymic IS NULL),
    birth_date DATE NOT NULL
        CONSTRAINT valid_birth_date CHECK (birth_date > '1900-01-01' AND birth_date <= current_date)
);
         """)
]
