"""

"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
         CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            login VARCHAR(32) UNIQUE NOT NULL,
            password VARCHAR(128) NOT NULL
                CONSTRAINT password_length CHECK (LENGTH(password) >= 8)
                CONSTRAINT password_uppercase CHECK (password ~ '[A-Z]')
                CONSTRAINT password_lowercase CHECK (password ~ '[a-z]')
                CONSTRAINT password_digit CHECK (password ~ '[0-9]')
                CONSTRAINT password_special CHECK (password ~ '[^A-Za-z0-9]'),
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                CONSTRAINT valid_registration_date CHECK (registration_date >= '2000-01-01' AND registration_date <= CURRENT_TIMESTAMP)
            );
         """),
    step("""
         CREATE UNIQUE INDEX idx_unique_user_login ON users (LOWER(login));
         """)
]
