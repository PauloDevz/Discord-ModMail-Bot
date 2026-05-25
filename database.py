import sqlite3
import os

class Database:
    def __init__(self, db_path="modmail.db"):
        # Se o diretório não existir, cria
        dir_name = os.path.dirname(db_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        # Conecta ao DB em modo leitura/escrita, cria se não existir
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        # Cria tabelas
        self.setup()
        print(f"[Database] Conectado em: {self.db_path}")

    def setup(self):
        # tabela de guilds
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS guilds (
            guild_id INTEGER PRIMARY KEY,
            category_id INTEGER,
            support_roles TEXT,
            log_channel INTEGER,
            open_message TEXT,
            first_reply TEXT,
            close_message TEXT
        )
        """)

        # tabela de tickets
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            user_id INTEGER,
            guild_id INTEGER,
            channel_id INTEGER,
            open INTEGER DEFAULT 1
        )
        """)
        self.conn.commit()

    # retorna ticket aberto
    def get_ticket(self, user_id, guild_id):
        return self.cur.execute(
            "SELECT * FROM tickets WHERE user_id=? AND guild_id=? AND open=1",
            (user_id, guild_id)
        ).fetchone()

    # cria novo ticket
    def create_ticket(self, user_id, guild_id, channel_id):
        try:
            self.cur.execute(
                "INSERT INTO tickets (user_id, guild_id, channel_id, open) VALUES (?, ?, ?, 1)",
                (user_id, guild_id, channel_id)
            )
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(f"[Database Error] Não foi possível criar o ticket: {e}")

    # fecha ticket
    def close_ticket(self, channel_id):
        try:
            self.cur.execute(
                "UPDATE tickets SET open=0 WHERE channel_id=?",
                (channel_id,)
            )
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(f"[Database Error] Não foi possível fechar o ticket: {e}")