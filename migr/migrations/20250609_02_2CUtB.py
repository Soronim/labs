"""

"""

from yoyo import step

__depends__ = {'20250609_01_NtjAd'}

steps = [
    step("""
         INSERT INTO tags (title) VALUES 
             ('pop'),
             ('rock'),
             ('hip-hop'),
             ('blues'),
             ('punk'),
             ('counrty'),
             ('metal');
         """)
]
