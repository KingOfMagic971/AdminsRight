# -*- coding: utf-8 -*-
# meta developer: @Gosgrrr
# scope: hikka_only

import sqlite3
import json
from .. import loader, utils

DB_FILE = "admin_rights.db"

DEFAULT_RIGHTS = {
    'info': 0, 'post': 0, 'edit': 0,
    'delete': 1, 'ban': 1, 'invite': 1,
    'pin': 1, 'add_admins': 0, 'anon': 0, 'call': 1,
    'poststory': 0, 'editstory': 0, 'delstory': 0
}

class AdminRightsConfig(loader.Module):
    """⚙️ Управление админскими правами и конфигами"""

    strings = {"name": "AdminRights"}

    async def client_ready(self, client, db):
        self.db = db
        self._init_db()
        self.rights = self._load_rights()

    # 📂 Инициализация базы
    def _init_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS admin_rights_config (
            right_name TEXT PRIMARY KEY,
            is_enabled INTEGER
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS admin_presets (
            name TEXT PRIMARY KEY,
            rights TEXT
        )''')
        cursor.execute("SELECT COUNT(*) FROM admin_rights_config")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                'INSERT INTO admin_rights_config (right_name, is_enabled) VALUES (?, ?)',
                list(DEFAULT_RIGHTS.items())
            )
        conn.commit()
        conn.close()

    # 🔄 Загрузка прав
    def _load_rights(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT right_name, is_enabled FROM admin_rights_config")
        rights = {row[0]: bool(row[1]) for row in cursor.fetchall()}
        conn.close()
        return rights

    # 💾 Сохранение права
    def _save_right(self, right_name, is_enabled):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO admin_rights_config (right_name, is_enabled) VALUES (?, ?)',
            (right_name, 1 if is_enabled else 0),
        )
        conn.commit()
        conn.close()
        self.rights[right_name] = is_enabled

    # 💾 Сохранение пресета
    def _save_preset(self, name):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO admin_presets (name, rights) VALUES (?, ?)',
            (name, json.dumps(self.rights)),
        )
        conn.commit()
        conn.close()

    # 🔄 Загрузка пресета
    def _load_preset(self, name):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT rights FROM admin_presets WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            rights = json.loads(row[0])
            for k, v in rights.items():
                self._save_right(k, v)
            return True
        return False

    # 📋 Форматированный список прав
    def _format_rights(self, rights=None):
        rights = rights or self.rights
        icons = {True: "✅", False: "❌"}
        names = {
            "info": "Изменение информации о группе",
            "post": "Публикация сообщений (для каналов)",
            "edit": "Редактирование чужих сообщений (для каналов)",
            "delete": "Удаление чужих сообщений",
            "ban": "Блокировка пользователей",
            "invite": "Приглашение пользователей",
            "pin": "Закрепление сообщений",
            "add_admins": "Добавление новых администраторов",
            "anon": "Анонимная отправка (в группах)",
            "call": "Управление видеочатами",
            "poststory": "Публикация историй",
            "editstory": "Редактирование историй",
            "delstory": "Удаление историй",
        }
        text = "🔄 Текущие права:\n\n"
        for right, enabled in rights.items():
            text += f"{icons[enabled]} `{right}` ({names[right]})\n"
        return text

    # 📌 Команды

    async def admincmd(self, message):
        """[preset] [rank] - показать права или применить пресет"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self._format_rights())
            return

        if len(args) >= 2:
            preset, rank = args[0], " ".join(args[1:])
            user = message.sender.first_name
            if self._load_preset(preset):
                await utils.answer(
                    message,
                    f"🛡 {user} назначен(а) администратором с званием «{rank}».",
                )
            else:
                await utils.answer(message, f"❌ Конфигурация «{preset}» не найдена.")

    async def adminsscmd(self, message):
        """<право> <on/off> - изменить право"""
        args = utils.get_args(message)
        if len(args) != 2:
            await utils.answer(message, "❌ Используй: .admins <право> <on/off>")
            return

        right, state = args
        if right not in self.rights:
            await utils.answer(message, f"❌ Неизвестное право: {right}")
            return

        is_enabled = state.lower() == "on"
        self._save_right(right, is_enabled)

        status = "ВКЛЮЧЕНО ✅" if is_enabled else "ВЫКЛЮЧЕНО ❌"
        await utils.answer(message, f"{status} право `{right}` для команды .admin.")

    async def adminsavecmd(self, message):
        """<имя> - сохранить текущую конфигурацию"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, "❌ Используй: .adminsave <имя>")
            return

        name = args[0]
        self._save_preset(name)
        await utils.answer(message, f"💾 Конфигурация «{name}» сохранена.")

    async def adminlistcmd(self, message):
        """- показать список сохранённых конфигураций"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM admin_presets")
        presets = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not presets:
            await utils.answer(message, "📋 Сохранённых конфигураций нет.")
            return

        text = "📋 Сохранённые конфигурации прав:\n\n"
        for name in presets:
            text += f"• {name}\n"
        await utils.answer(message, text)

    async def adminshowcmd(self, message):
        """<имя> - показать содержимое конфигурации"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, "❌ Используй: .adminshow <имя>")
            return

        name = args[0]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT rights FROM admin_presets WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            await utils.answer(message, f"❌ Конфигурация «{name}» не найдена.")
            return

        rights = json.loads(row[0])
        await utils.answer(message, f"📋 Конфигурация **{name}**:\n\n" + self._format_rights(rights))

    async def admindelcmd(self, message):
        """<имя> - удалить конфигурацию"""
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, "❌ Используй: .admindel <имя>")
            return

        name = args[0]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admin_presets WHERE name = ?", (name,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()

        if deleted:
            await utils.answer(message, f"🗑 Конфигурация «{name}» удалена.")
        else:
            await utils.answer(message, f"❌ Конфигурация «{name}» не найдена.")

    async def adminrenamecmd(self, message):
        """<старое> <новое> - переименовать конфигурацию"""
        args = utils.get_args(message)
        if len(args) != 2:
            await utils.answer(message, "❌ Используй: .adminrename <старое> <новое>")
            return

        old, new = args
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE admin_presets SET name = ? WHERE name = ?", (new, old))
        conn.commit()
        updated = cursor.rowcount
        conn.close()

        if updated:
            await utils.answer(message, f"✏️ Конфигурация «{old}» переименована в «{new}».")
        else:
            await utils.answer(message, f"❌ Конфигурация «{old}» не найдена.")