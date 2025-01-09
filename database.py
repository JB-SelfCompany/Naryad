import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='naryad.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Установка соединения с базой данных"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Создание необходимых таблиц"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS naryad (
                shifr TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                workshop_number INTEGER NOT NULL,
                employee_number INTEGER NOT NULL,
                operation_code TEXT NOT NULL,
                time_norm REAL NOT NULL,
                parts_count INTEGER NOT NULL
            )
        ''')
        self.conn.commit()

    def add_record(self, shifr, date, workshop_number, employee_number, 
                  operation_code, time_norm, parts_count):
        """Добавление новой записи"""
        try:
            self.cursor.execute('''
                INSERT INTO naryad VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (shifr, date, workshop_number, employee_number, 
                 operation_code, time_norm, parts_count))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_record(self, shifr):
        """Удаление записи по шифру"""
        self.cursor.execute('DELETE FROM naryad WHERE shifr = ?', (shifr,))
        self.conn.commit()

    def update_record(self, shifr, date, workshop_number, employee_number, 
                     operation_code, time_norm, parts_count):
        """Обновление существующей записи"""
        self.cursor.execute('''
            UPDATE naryad 
            SET date = ?, workshop_number = ?, employee_number = ?, 
                operation_code = ?, time_norm = ?, parts_count = ?
            WHERE shifr = ?
        ''', (date, workshop_number, employee_number, operation_code, 
              time_norm, parts_count, shifr))
        self.conn.commit()

    def search_records(self, **kwargs):
        """Поиск записей по различным параметрам"""
        query = 'SELECT * FROM naryad WHERE 1=1'
        params = []
        
        for key, value in kwargs.items():
            if value:
                query += f' AND {key} = ?'
                params.append(value)
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_all_records(self):
        """Получение всех записей"""
        self.cursor.execute('SELECT * FROM naryad')
        return self.cursor.fetchall()

    def get_workshop_productivity(self, start_date, end_date):
        """Получение производительности цехов за период"""
        self.cursor.execute('''
            SELECT workshop_number, 
                   SUM(parts_count) as total_parts,
                   AVG(parts_count * 1.0 / time_norm) as productivity
            FROM naryad
            WHERE date BETWEEN ? AND ?
            GROUP BY workshop_number
            ORDER BY productivity DESC
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def get_operation_complexity(self):
        """Получение трудоемкости операций"""
        self.cursor.execute('''
            SELECT operation_code,
                   AVG(time_norm) as avg_time,
                   COUNT(*) as operation_count
            FROM naryad
            GROUP BY operation_code
            ORDER BY avg_time DESC
        ''')
        return self.cursor.fetchall()

    def get_orders_by_period(self, period_type):
        """Получение количества нарядов по периодам"""
        if period_type == 'year':
            date_format = '%Y'
        elif period_type == 'month':
            date_format = '%Y-%m'
        else:  # day
            date_format = '%Y-%m-%d'
        
        query = f'''
            SELECT strftime('{date_format}', date) as period,
                   COUNT(*) as order_count
            FROM naryad
            GROUP BY period
            ORDER BY period
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
