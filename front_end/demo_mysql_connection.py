import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="craft",
  passwd="craft"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE mydatabase")