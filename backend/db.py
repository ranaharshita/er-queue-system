import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",        # default XAMPP username
        password="",        # default XAMPP password is empty
        database="er_queue"
    )
    return connection