# -- coding: utf-8 --
# meta developer: @Gosgrrr
# scope: hikka_only

__version__ = (0, 0, 78)

from .. import loader, utils
from telethon.tl.types import ChatAdminRights

@loader.tds
class AdminConfigurator(loader.Module):
    """Гибкая настройка прав админов с конфигурациями"""

    strings = {
        "name": "AdminConfigurator",
        "rights": "<blockquote><emoji document_id=5258420634785947640>🔄</emoji> Current rights:\n\n{}</blockquote>",
        "saved": "<blockquote><emoji document_id=5258453452631056344>✅️</emoji> Configuration <b>{}</b> saved.</blockquote>",
        "loaded": "<blockquote><emoji document_id=5251203410396458957>🛡</emoji> {} appointed as administrator with title «{}».</blockquote>",
        "not_found": "<blockquote><emoji document_id=5258331647358540449>✍️</emoji> Configuration <b>{}</b> not found.</blockquote>",
        "list": "<blockquote><emoji document_id=5258331647358540449>✍️</emoji> Saved rights configurations:\n\n{}</blockquote>",
        "deleted": "<blockquote><emoji document_id=5258130763148172425>🗑</emoji> Configuration <b>{}</b> deleted.</blockquote>",
        "renamed": "<blockquote><emoji document_id=5197269100878907942>✏️</emoji> Configuration <b>{}</b> renamed to <b>{}</b>.</blockquote>",
        "unadmin": "<blockquote><emoji document_id=5258453452631056344>✅️</emoji> <b>All rights and title removed from user {} successfully.</b></blockquote>",
        "invalid_admins_usage": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Use: <code>{prefix}admins (right) (on/off)</code></blockquote>",
        "unknown_right": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Unknown right: <code>{}</code></blockquote>",
        "invalid_admin_usage": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Use: <code>{prefix}admin (config) (username/id/reply) (title)</code></blockquote>",
        "admin_error": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Error: {}</blockquote>",
        "no_config_name": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Specify the configuration name</blockquote>",
        "no_configs": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> No saved configurations</blockquote>",
        "invalid_rename_usage": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Use: <code>{prefix}adminrename (old) (new)</code></blockquote>",
        "invalid_unadmin_usage": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Specify username/id or reply to a message</blockquote>",
    }

    strings_ru = {
        "name": "AdminConfigurator",
        "rights": "<blockquote><emoji document_id=5258420634785947640>🔄</emoji> Текущие права:\n\n{}</blockquote>",
        "saved": "<blockquote><emoji document_id=5258453452631056344>✅️</emoji> Конфигурация <b>{}</b> сохранена.</blockquote>",
        "loaded": "<blockquote><emoji document_id=5251203410396458957>🛡</emoji> {} назначен(а) администратором с званием «{}».</blockquote>",
        "not_found": "<blockquote><emoji document_id=5258331647358540449>✍️</emoji> Конфигурация <b>{}</b> не найдена.</blockquote>",
        "list": "<blockquote><emoji document_id=5258331647358540449>✍️</emoji> Сохраненные конфигурации прав:\n\n{}</blockquote>",
        "deleted": "<blockquote><emoji document_id=5258130763148172425>🗑</emoji> Конфигурация <b>{}</b> удалена.</blockquote>",
        "renamed": "<blockquote><emoji document_id=5197269100878907942>✏️</emoji> Конфигурация <b>{}</b> переименована в <b>{}</b>.</blockquote>",
        "unadmin": "<blockquote><emoji document_id=5258453452631056344>✅️</emoji> <b>Все права и звание с пользователя {} успешно сняты.</b></blockquote>",
        "invalid_admins_usage": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Используй: <code>{prefix}admins (право) (on/off)</code></blockquote>",
        "unknown_right": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Неизвестное право: <code>{}</code></blockquote>",
        "invalid_admin_usage": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Используй: <code>{prefix}admin (конфиг) (username/id/reply) (звание)</code></blockquote>",
        "admin_error": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Ошибка: {}</blockquote>",
        "no_config_name": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Укажи название конфигурации</blockquote>",
        "no_configs": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Нет сохранённых конфигураций</blockquote>",
        "invalid_rename_usage": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Используй: <code>{prefix}adminrename (старое) (новое)</code></blockquote>",
        "invalid_unadmin_usage": "<blockquote><emoji document_id=5260342697075416641>❌</emoji> Укажи username/id или ответь на сообщение</blockquote>",
    }

    async def client_ready(self, client, db):
        self.client = client
        self._db = db
        self.prefix = self.get_prefix()
        self.configs = self._db.get("AdminConfigurator", "configs", {})
        self.current = {k: False for k in await self._all_rights()}
        self.rank = "админ"

    async def _all_rights(self):
        return {
            "info": "Изменение информации о группе",
            "post": "Публикация сообщений (для каналов)",
            "edit": "Редактирование чужих сообщений (для каналов)",
            "add_admins": "Добавление новых администраторов",
            "anon": "Анонимная отправка (в группах)",
            "poststory": "Публикация историй",
            "editstory": "Редактирование историй",
            "delstory": "Удаление историй",
            "call": "Управление видеочатами",
            "delete": "Удаление чужих сообщений",
            "ban": "Блокировка пользователей",
            "pin": "Закрепление сообщений",
            "invite": "Приглашение пользователей",
        }

    async def _format_rights(self):
        lines = []
        for key, desc in (await self._all_rights()).items():
            state = "<emoji document_id=5258453452631056344>✅️</emoji>" if self.current.get(key, False) else "<emoji document_id=5260342697075416641>❌</emoji>"
            lines.append(f"{state} <code>{key}</code> ({desc})")
        return self.strings["rights"].format("\n".join(lines))

    async def _to_rights(self):
        return ChatAdminRights(
            change_info=self.current["info"],
            post_messages=self.current["post"],
            edit_messages=self.current["edit"],
            add_admins=self.current["add_admins"],
            anonymous=self.current["anon"],
            manage_call=self.current["call"],
            delete_messages=self.current["delete"],
            ban_users=self.current["ban"],
            pin_messages=self.current["pin"],
            invite_users=self.current["invite"],
        )

    async def _save(self):
        self._db.set("AdminConfigurator", "configs", self.configs)

    @loader.command(ru_doc="(право) (on/off) — включить/выключить право", en_doc="(right) (on/off) — enable/disable a right")
    async def admins(self, message):
        args = utils.get_args(message)
        if len(args) != 2:
            return await utils.answer(message, self.strings["invalid_admins_usage"].format(prefix=self.prefix))

        key, state = args[0], args[1].lower()
        if key not in await self._all_rights():
            return await utils.answer(message, self.strings["unknown_right"].format(key))

        self.current[key] = state == "on"
        await utils.answer(message, await self._format_rights())

    @loader.command(ru_doc="(конфиг) (username/id/reply) (звание) — применить конфиг", en_doc="(config) (username/id/reply) (title) — apply config")
    async def admin(self, message):
        args = utils.get_args(message)
        if len(args) < 3:
            return await utils.answer(message, self.strings["invalid_admin_usage"].format(prefix=self.prefix))

        preset, target, rank = args[0], args[1], " ".join(args[2:])
        if preset not in self.configs:
            return await utils.answer(message, self.strings["not_found"].format(preset))

        user = await utils.get_user(message, target)
        rights = ChatAdminRights(**self.configs[preset])
        try:
            await self.client.edit_admin(message.chat_id, user.id, rights, rank)
            await utils.answer(message, self.strings["loaded"].format(utils.escape_html(user.first_name), rank))
        except Exception as e:
            await utils.answer(message, self.strings["admin_error"].format(e))

    @loader.command(ru_doc="(название) — сохранить текущую конфигурацию", en_doc="(name) — save the current configuration")
    async def adminsave(self, message):
        args = utils.get_args(message)
        if not args:
            return await utils.answer(message, self.strings["no_config_name"])
        name = args[0]
        self.configs[name] = self.current.copy()
        await self._save()
        await utils.answer(message, self.strings["saved"].format(name))

    @loader.command(ru_doc="— показать список сохранённых конфигураций", en_doc="— show list of saved configurations")
    async def adminlist(self, message):
        if not self.configs:
            return await utils.answer(message, self.strings["no_configs"])
        text = "\n".join([f"• <b>{name}</b>" for name in self.configs])
        await utils.answer(message, self.strings["list"].format(text))

    @loader.command(ru_doc="(название) — показать права конфигурации", en_doc="(name) — show rights of a configuration")
    async def adminshow(self, message):
        args = utils.get_args(message)
        if not args:
            return await utils.answer(message, self.strings["no_config_name"])
        name = args[0]
        if name not in self.configs:
            return await utils.answer(message, self.strings["not_found"].format(name))
        conf = self.configs[name]
        lines = []
        for key, desc in (await self._all_rights()).items():
            state = "<emoji document_id=5258453452631056344>✅️</emoji>" if conf.get(key, False) else "<emoji document_id=5260342697075416641>❌</emoji>"
            lines.append(f"{state} <code>{key}</code> ({desc})")
        await utils.answer(message, f"<blockquote><emoji document_id=5258096772776991776>⚙</emoji> Конфигурация <b>{name}</b>:\n\n" + "\n".join(lines) + "</blockquote>")

    @loader.command(ru_doc="(название) — удалить конфигурацию", en_doc="(name) — delete a configuration")
    async def admindelete(self, message):
        args = utils.get_args(message)
        if not args:
            return await utils.answer(message, self.strings["no_config_name"])
        name = args[0]
        if name not in self.configs:
            return await utils.answer(message, self.strings["not_found"].format(name))
        del self.configs[name]
        await self._save()
        await utils.answer(message, self.strings["deleted"].format(name))

    @loader.command(ru_doc="(старое) (новое) — переименовать конфигурацию", en_doc="(old) (new) — rename a configuration")
    async def adminrename(self, message):
        args = utils.get_args(message)
        if len(args) < 2:
            return await utils.answer(message, self.strings["invalid_rename_usage"].format(prefix=self.prefix))
        old, new = args[0], args[1]
        if old not in self.configs:
            return await utils.answer(message, self.strings["not_found"].format(old))
        self.configs[new] = self.configs.pop(old)
        await self._save()
        await utils.answer(message, self.strings["renamed"].format(old, new))

    @loader.command(ru_doc="(username/id/reply) — снять все права", en_doc="(username/id/reply) — remove all rights")
    async def unadmin(self, message):
        args = utils.get_args(message)
        if not args and not message.is_reply:
            return await utils.answer(message, self.strings["invalid_unadmin_usage"])

        target = args[0] if args else None
        user = await utils.get_user(message, target)
        rights = ChatAdminRights(
            change_info=False,
            post_messages=False,
            edit_messages=False,
            add_admins=False,
            anonymous=False,
            manage_call=False,
            delete_messages=False,
            ban_users=False,
            pin_messages=False,
            invite_users=False,
        )
        try:
            await self.client.edit_admin(message.chat_id, user.id, rights, "")
            await utils.answer(message, self.strings["unadmin"].format(utils.escape_html(user.first_name)))
        except Exception as e:
            await utils.answer(message, self.strings["admin_error"].format(e))
