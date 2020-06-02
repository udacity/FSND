import os
import psycopg2

password_path = os.path.dirname(os.path.abspath(__file__)) + '/../../.dbpassword'
print('password_path: {}'.format(password_path))

with open(password_path) as fp:
    password = fp.read()

print("password: {}".format(password))

conn = psycopg2.connect('dbname=test_psycopg2 user=frank password={}'.format(password))

cursor = conn.cursor()

# Open a cursor to perform database operations
cur = conn.cursor()

# drop any existing todos table
cur.execute("DROP TABLE IF EXISTS todos;")

# (re)create the todos table
# (note: triple quotes allow multiline text in python)
cur.execute("""
  CREATE TABLE todos (
    id serial PRIMARY KEY,
    description VARCHAR NOT NULL
  );
""")

cur.execute("""
    INSERT INTO todos ( description )
    VALUES ('do some udacity'), ('learn some good stuff'), ('get better at things');

""")

cur.execute(""" SELECT * from todos;""")
result = cur.fetchall()
print("fetched all: ")
print("result\n{}".format(result))
result = cur.fetchone()
print("fetched one: ")
print("result\n{}".format(result))

print("committing")
# commit, so it does the executions on the db and persists in the db
conn.commit()

cur.execute(""" SELECT * from todos;""")
result = cur.fetchone()
print("fetched one: ")
print("result\n{}".format(result))

cur.close()
conn.close()