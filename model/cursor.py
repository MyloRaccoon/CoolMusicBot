import sqlite3
import os
import dotenv

dotenv.load_dotenv()
BDD_PATH = os.getenv("BDD_PATH")

con = sqlite3.connect(BDD_PATH)
cur = con.cursor()