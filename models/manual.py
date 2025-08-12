from config import db

def insert_manual(manual_data):
    return db.manuals.insert_one(manual_data)

def find_manual(query):
    return db.manuals.find_one(query)