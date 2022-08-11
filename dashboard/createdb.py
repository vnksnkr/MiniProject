import sqlite3  
  
con = sqlite3.connect("tremors.db")  
print("Database opened successfully")  
  
con.execute("create table Tremors (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, acc_x REAL  NOT NULL, acc_y REAL NOT NULL, acc_z REAL NOT NULL)")  
  
print("Table created successfully")  
  
con.close()  