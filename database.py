import sqlite3
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = 'vpn_bot.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                ref_code TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan TEXT NOT NULL,
                price INTEGER NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                devices_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscription_id INTEGER NOT NULL,
                device_name TEXT,
                config TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bonuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER,
                ref_code TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bonus_given BOOLEAN DEFAULT 0,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                FOREIGN KEY (referred_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, first_name: str, username: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            ref_code = f"VPN{user_id}{uuid.uuid4().hex[:6].upper()}"
            cursor.execute('''INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)''', 
                         (user_id, username, first_name, ref_code))
            cursor.execute('''INSERT OR IGNORE INTO bonuses (user_id, amount) VALUES (?, 0)''', (user_id,))
            conn.commit()
            return ref_code
        finally:
            conn.close()
    
    def get_user_ref_code(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT ref_code FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['ref_code'] if result else None
        finally:
            conn.close()
    
    def create_subscription(self, user_id: int, plan: str, price: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            start_date = datetime.now()
            days = {'1_month': 30, '3_months': 90, '6_months': 180, '12_months': 365}.get(plan, 30)
            end_date = start_date + timedelta(days=days)
            cursor.execute('''INSERT INTO subscriptions (user_id, plan, price, end_date) VALUES (?, ?, ?, ?)''',
                         (user_id, plan, price, end_date))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_active_subscription(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''SELECT * FROM subscriptions WHERE user_id = ? AND is_active = 1 
                            AND end_date > datetime('now') LIMIT 1''', (user_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    
    def add_device(self, subscription_id: int, device_name: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) as count FROM devices WHERE subscription_id = ?', (subscription_id,))
            if cursor.fetchone()['count'] >= 3:
                return False, "Максимум 3 устройства!"
            cursor.execute('''INSERT INTO devices (subscription_id, device_name) VALUES (?, ?)''', 
                         (subscription_id, device_name))
            cursor.execute('''UPDATE subscriptions SET devices_count = devices_count + 1 WHERE id = ?''', (subscription_id,))
            conn.commit()
            return True, "Добавлено!"
        finally:
            conn.close()
    
    def get_bonuses(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT amount FROM bonuses WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result['amount'] if result else 0
        finally:
            conn.close()
    
    def add_bonus(self, user_id: int, amount: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE bonuses SET amount = amount + ? WHERE user_id = ?', (amount, user_id))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_referrer_by_code(self, ref_code: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT user_id FROM users WHERE ref_code = ?', (ref_code,))
            result = cursor.fetchone()
            return result['user_id'] if result else None
        finally:
            conn.close()
    
    def add_referral(self, referrer_id: int, referred_id: int, ref_code: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO referrals (referrer_id, referred_id, ref_code) VALUES (?, ?, ?)''',
                         (referrer_id, referred_id, ref_code))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def apply_referral_bonus(self, referrer_id: int, price: int):
        bonus = int(price * 0.1)
        return self.add_bonus(referrer_id, bonus)
