--- 
description :   Create a single dummy user in the database
allowed-tools:  Read, Bash(python3:*)
---

Read database/db.py to understand users table schema and the get_db() helper.
1. Generate a realistic  random indian user 
    - email : derived from name with a sharma91@gmail.com
    - password: "password123" hashed with werzeug's generate_password_hash
    - created_at: current datetime

2. checks if the generated email already exists in the users table. if it does, regenerate untill unique.
3. insert the users into database using the same get_db() pattern found in db.py.
4. print confirmatio:
    - id
    - name
    - email
    