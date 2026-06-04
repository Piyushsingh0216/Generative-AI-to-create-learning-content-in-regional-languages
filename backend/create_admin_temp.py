import os
import sqlite3
from passlib.context import CryptContext

ctx = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
h = ctx.hash('AdminPass123!')

db = 'learning_platform.db'
print('db path', os.path.abspath(db), os.path.exists(db))
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute('select id,email,is_admin from users where email=?', ('admin@example.com',))
row = cur.fetchone()
print('before', row)
if not row:
    cur.execute(
        'insert into users(email,hashed_password,full_name,is_admin,time_spent_seconds,summaries_generated,topics_learned) values(?,?,?,?,?,?,?)',
        ('admin@example.com', h, 'Admin User', 1, 0, 0, '[]'),
    )
    con.commit()
    cur.execute('select id,email,is_admin from users where email=?', ('admin@example.com',))
    print('after', cur.fetchone())
else:
    print('already exists')
con.close()
