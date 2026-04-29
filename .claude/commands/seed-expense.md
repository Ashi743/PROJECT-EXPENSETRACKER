---
description: Seed realistic dummy expenses for a specific user
argument-hint: "<user_id> <count> <months>"
allowed-tools: Read, Bash(python3:*)
---

Read database/db.py to understand the expenses table schema ,  the db connection pattern and the database file name.

User input : $ARGUMENTS 

## Step 1 - Parse arguemnts
Extract from $ARGUMENTS :
 - user_id - integer
 - count   - integer, number of expenses to create
 - months  - integer, how many past months you spread that expense across

if any argument is missing or not a valid integer, stop and say:
    "usage: /seed-expenses <user_id> <count> <months>  example: /seed-expenses 1 50 6"

## Step 2 - Verify user exists
Before generating anything ,confirm the user_id exists in the query table. If not , stop and say:
    "No user found with id <user_id>


## Step 3 - Generate and insert expenses
Write and run a python script that:
1. spread the expenses randomly across months <months> 
2. uses these categories with realistic indian descriptions and amounts:
    - food : 50-800
    - transport: 20-500
    - bills: 200-3000
    - health: 100-2000
    - entertainment: 100-1500
    - shopping : 200-5000
    - other: 50-1000
3. distribute categories roughly proportionatly ( food most common, health and entertainment least common)
4. use the db connection pattern from db.py  - do not  hardcode the database file
5. uses parameterized queries only - no string formatting in sql.
6. insert all expenses in single transactions -  roll back everything if any insert fails

## Step 4 -  Confirm
Print:
    - hown many expenses were inserted
    - the date range they span
    - a sample of 5 inserted records