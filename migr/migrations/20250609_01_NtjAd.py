from yoyo import step

__depends__ = {'20250518_02_oxNJi', '20250519_01_bOjbp'}

steps = [
    step("""
         CREATE EXTENSION IF NOT EXISTS citext;
         
         CREATE TABLE tags (
             id SERIAL PRIMARY KEY,
             title CITEXT NOT NULL
                 CONSTRAINT no_leading_trailing_spaces CHECK (title = trim(title))
                 CONSTRAINT no_double_spaces CHECK (title !~ '\s{2}')
                 CONSTRAINT unique_title_case_insensitive UNIQUE
         );
         """),
    step("""
         CREATE OR REPLACE FUNCTION add_tag_to_account(
             p_user_id INTEGER,
             p_tag_id INTEGER
         ) RETURNS VOID AS $$
         BEGIN
             IF NOT EXISTS (SELECT 1 FROM tags WHERE id = p_tag_id) THEN
                 RAISE EXCEPTION 'Tag with id % does not exist', p_tag_id;
             END IF;
             
             UPDATE accounts 
             SET tags = array_append(tags, p_tag_id)
             WHERE user_id = p_user_id;
         END;
         $$ LANGUAGE plpgsql;
         """),
    step("""
         CREATE OR REPLACE FUNCTION remove_tag_from_account(
             p_user_id INTEGER,
             p_tag_id INTEGER
         ) RETURNS VOID AS $$
         BEGIN
             UPDATE accounts 
             SET tags = array_remove(tags, p_tag_id)
             WHERE user_id = p_user_id;
         END;
         $$ LANGUAGE plpgsql;
         """),
    step("""
         CREATE OR REPLACE FUNCTION delete_tag(
             p_tag_id INTEGER
         ) RETURNS VOID AS $$
         BEGIN
             -- Удаляем тег из всех аккаунтов
             UPDATE accounts 
             SET tags = array_remove(tags, p_tag_id);
             
             -- Удаляем сам тег
             DELETE FROM tags WHERE id = p_tag_id;
         END;
         $$ LANGUAGE plpgsql;
         """)
]