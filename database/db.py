import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS quests("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "author_id INTEGER, "
                            "quest_id TEXT,"
                            "locked BOOLEAN, "
                            "name TEXT, "
                            "desc TEXT,"
                            "final TEXT,"
                            "final_content_id TEXT,"
                            "correct_msg TEXT,"
                            "wrong_msg TEXT"
                            ")"
                            )
        self.cursor.execute("CREATE TABLE IF NOT EXISTS steps("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "quest_id TEXT,"
                            "num INTEGER,"
                            "text TEXT,"
                            "answer TEXT,"
                            "content_id TEXT,"
                            "hint TEXT"
                            ")"
                            )
        self.conn.commit()

    def close(self):
        self.conn.close()
