import sqlite3
import time
import math


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, 1, NULL, ?)", (email, hpsw, name, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False

        return True

    def change_task(self, task_id, task, desc, importance):
        try:
            self.__cur.execute(f"UPDATE tasks SET task = ?, description = ?, importance = ? WHERE id = ?", (task, desc, importance, task_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления информации в БД: " + str(e))
            return False
        return True

    def getTaskById(self, task_id):
        try:
            self.__cur.execute(f"SELECT task FROM tasks WHERE id = '{task_id}'")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return False, False

    def getDescriptionById(self, task_id):
        try:
            self.__cur.execute(f"SELECT description FROM tasks WHERE id = '{task_id}'")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return False, False

    def getImportanceById(self, task_id):
        try:
            self.__cur.execute(f"SELECT importance FROM tasks WHERE id = '{task_id}'")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return False, False

    def delete_task(self, task_id):
        try:
            self.__cur.execute(f"DELETE FROM tasks WHERE id == '{task_id}'")
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))
        return False

    def delete_user(self, user_id):
        try:
            self.__cur.execute(f"DELETE FROM users WHERE id =='{user_id}'")
            self.__cur.execute(f"DELETE FROM tasks WHERE user_id =='{user_id}'")
            self.__db.commit()
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))
        return False

    def getStartMenu(self):
        sql = '''SELECT * FROM startmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def getAdminMenu(self):
        sql = ''' SELECT * FROM adminmenu '''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def getAllTasks(self):
        try:
            self.__cur.execute(f"SELECT id, task, description, importance FROM tasks ORDER BY importance DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return []

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: "+str(e))
            return False
        return True

    def getIdUserFromIdTask(self, task_id):
        try:
            self.__cur.execute(f"SELECT user_id FROM tasks WHERE id = '{task_id}'")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return False, False

    def getAllTasksFromID(self, id_user):
        try:
            self.__cur.execute(f"SELECT id, task, description, importance FROM tasks WHERE user_id = '{id_user}' AND status = 'В процессе'")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return False, False

    def getUserMenu(self):
        sql = ''' SELECT * FROM usermenu '''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = '{user_id}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def getSortedTasksByTime(self, id_user):
        try:
            self.__cur.execute(f"SELECT id, task, description, importance FROM tasks WHERE user_id = '{id_user}' AND status = 'В процессе' ORDER BY time ASC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ощибка получения статьи из БД " + str(e))
        return False, False

    def setTaskComplete(self, task_id):
        try:
            status = "Выполнено"
            self.__cur.execute(f"UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: "+str(e))
            return False
        return True

    def getSortedTasksByImp(self, id_user):
        try:
            self.__cur.execute(f"SELECT id, task, description, importance FROM tasks WHERE user_id = '{id_user}' ORDER BY importance DESC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return False, Fals

    def getAllUsersExceptAdmin(self):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE usertype = '1'")
            res = self.__cur.fetchall()
            if not res:
                print("Пользователи не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД " + str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))

        return False

    def addTask(self, task, disc, imp, id_user):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM tasks WHERE task LIKE '{task}' AND status = 'В процессе'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Такое задание уже существует")
                return False

            # base = url_for('static', filename='images_html')

            # text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
            #               "\\g<tag>" + base + "/\\g<url>>",
            #               text)

            tm = math.floor(time.time())
            status = 'В процессе'
            self.__cur.execute("INSERT INTO tasks VALUES(NULL, ?, ?, ?, ?, ?, ?)",
                               (task, imp, status, id_user, disc, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД " + str(e))
            return False

        return True
