from hikkatl.types import Message
from .. import loader, utils
from telethon.tl.types import PeerChannel

@loader.tds
class MyModule(loader.Module):
    """My module"""
    strings = {
        "name": "MyModule",
        "hello": "Hello world!",
        "user_set_by_username": "User {0} set for monitoring ({1})",
        "user_not_found": "User {0} not found",
        "user_set_by_id": "User ID {0} set for monitoring ({1})",
        "invalid_user_id": "Please provide a valid user ID",
        "list_cleared": "Monitored users list cleared",
        "monitoring_users": "Monitored users: {0}",
        "no_users": "No users are being monitored",
        "group_created": "Group {0} created for logging",
        "group_set": "Group {0} set for logging",
        "current_group": "Current logging group: {0}",
        "no_group_set": "No logging group is set"
    }

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self.monitored_users = self._db.get("MyModule", "monitored_users", [])
        self.logging_group = self._db.get("MyModule", "logging_group", None)

    @loader.command(
        ru_doc="Устанавливает пользователя для мониторинга по тегу с указанием заметки",
    )
    async def stuser(self, message: Message):
        """Sets the user to monitor by username with a note"""
        args = utils.get_args(message)
        if len(args) < 2:
            return await utils.answer(message, "Please provide a username and a note")
        
        username = args[0]
        note = ' '.join(args[1:])
        try:
            user = await self._client.get_entity(username)
            self.monitored_users.append({"id": user.id, "note": note})
            self._db.set("MyModule", "monitored_users", self.monitored_users)
            await utils.answer(message, self.strings("user_set_by_username").format(username, note))
        except ValueError:
            await utils.answer(message, self.strings("user_not_found").format(username))

    @loader.command(
        ru_doc="Устанавливает ID пользователя для мониторинга с указанием заметки",
    )
    async def siuser(self, message: Message):
        """Sets the user ID to monitor with a note"""
        args = utils.get_args(message)
        if len(args) < 2:
            return await utils.answer(message, "Please provide a user ID and a note")
        
        try:
            user_id = int(args[0])
            note = ' '.join(args[1:])
            self.monitored_users.append({"id": user_id, "note": note})
            self._db.set("MyModule", "monitored_users", self.monitored_users)
            await utils.answer(message, self.strings("user_set_by_id").format(user_id, note))
        except ValueError:
            await utils.answer(message, self.strings("invalid_user_id"))

    @loader.command(
        ru_doc="Очищает список отслеживаемых пользователей",
    )
    async def clearusers(self, message: Message):
        """Clears the list of monitored users"""
        self.monitored_users = []
        self._db.set("MyModule", "monitored_users", self.monitored_users)
        await utils.answer(message, self.strings("list_cleared"))

    @loader.command(
        ru_doc="Показывает список отслеживаемых пользователей",
    )
    async def showusers(self, message: Message):
        """Shows the list of monitored users"""
        if not self.monitored_users:
            return await utils.answer(message, self.strings("no_users"))
        
        users_list = "\n".join([f"{user['id']} ({user['note']})" for user in self.monitored_users])
        await utils.answer(message, self.strings("monitoring_users").format(users_list))

    @loader.command(
        ru_doc="Создает группу для логирования",
    )
    async def cguser(self, message: Message):
        """Creates a group for logging"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "Please provide a group name")
        
        result = await self._client(functions.messages.CreateChatRequest(
            users=["me"],
            title=args
        ))
        group_id = result.chats[0].id
        self._db.set("MyModule", "logging_group", group_id)
        self.logging_group = group_id
        await utils.answer(message, self.strings("group_created").format(args))

    @loader.command(
        ru_doc="Устанавливает группу для логирования",
    )
    async def setgroup(self, message: Message):
        """Sets the group for logging"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "Please provide a group ID")
        
        try:
            group_id = int(args)
            self._db.set("MyModule", "logging_group", group_id)
            self.logging_group = group_id
            await utils.answer(message, self.strings("group_set").format(group_id))
        except ValueError:
            await utils.answer(message, "Please provide a valid group ID")

    @loader.command(
        ru_doc="Показывает текущую группу для логирования",
    )
    async def showgroup(self, message: Message):
        """Shows the current group for logging"""
        if self.logging_group:
            await utils.answer(message, self.strings("current_group").format(self.logging_group))
        else:
            await utils.answer(message, self.strings("no_group_set"))
