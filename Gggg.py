from telethon import events, functions, types
from hikkatl.types import Message
from .. import loader, utils

@loader.tds
class OnlineMonitorMod(loader.Module):
    """Monitors online status of a user"""
    strings = {
        "name": "OnlineMonitorMod",
        "user_tag": "Monitoring user: {}",
        "monitor_enabled": "Monitoring enabled",
        "monitor_disabled": "Monitoring disabled",
        "user_set_by_username": "User set for monitoring by username: {}",
        "user_set_by_id": "User set for monitoring by ID: {}",
        "user_not_found": "User not found: {}",
        "invalid_user_id": "Invalid user ID"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "user_id",
                None,
                "ID of the user to monitor",
                validator=loader.validators.TelegramID(),
            ),
            loader.ConfigValue(
                "monitoring_enabled",
                False,
                "Whether monitoring is enabled",
                validator=loader.validators.Boolean(),
            ),
        )
        self._chat_id = None
        self._monitoring_handler = None

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._me = await client.get_me()

        # Check if the group already exists
        existing_chat = await self.find_existing_chat("Online Status Logs")
        if existing_chat:
            self._chat_id = existing_chat.id
        else:
            # Create a new group for logging
            result = await client(functions.messages.CreateChatRequest(
                users=["me"],
                title="Online Status Logs"
            ))
            self._chat_id = result.chats[0].id

        # Add event handler for Raw updates if monitoring is enabled
        if self.config["monitoring_enabled"]:
            self._monitoring_handler = self._client.add_event_handler(self.on_raw_update, events.Raw)

    async def find_existing_chat(self, title):
        dialogs = await self._client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_group and dialog.title == title:
                return dialog
        return None

    async def on_raw_update(self, event):
        if isinstance(event, types.UpdateUserStatus):
            if event.user_id == self.config["user_id"]:
                if isinstance(event.status, types.UserStatusOnline):
                    await self._client.send_message(self._chat_id, f"User {self.config['user_id']} is now online")
                elif isinstance(event.status, types.UserStatusOffline):
                    await self._client.send_message(self._chat_id, f"User {self.config['user_id']} is now offline")

    @loader.command(
        ru_doc="Устанавливает пользователя для мониторинга по тегу",
    )
    async def stuser(self, message: Message):
        """Sets the user to monitor by username"""
        args = utils.get_args(message)
        if not args:
            return await utils.answer(message, "Please provide a username")
        
        username = args[0]
        try:
            user = await self._client.get_entity(username)
            self.config["user_id"] = user.id
            await utils.answer(message, self.strings("user_set_by_username").format(username))
        except ValueError:
            await utils.answer(message, self.strings("user_not_found").format(username))

    @loader.command(
        ru_doc="Устанавливает ID пользователя для мониторинга",
    )
    async def siuser(self, message: Message):
        """Sets the user ID to monitor"""
        args = utils.get_args(message)
        if not args:
            return await utils.answer(message, "Please provide a user ID")
        
        try:
            user_id = int(args[0])
            self.config["user_id"] = user_id
            await utils.answer(message, self.strings("user_set_by_id").format(user_id))
        except ValueError:
            await utils.answer(message, self.strings("invalid_user_id"))

    @loader.command(
        ru_doc="Включает или выключает отслеживание",
    )
    async def mt(self, message: Message):
        """Enables or disables monitoring"""
        if self.config["monitoring_enabled"]:
            self._client.remove_event_handler(self._monitoring_handler)
            self.config["monitoring_enabled"] = False
            await utils.answer(message, self.strings("monitor_disabled"))
        else:
            self._monitoring_handler = self._client.add_event_handler(self.on_raw_update, events.Raw)
            self.config["monitoring_enabled"] = True
            await utils.answer(message, self.strings("monitor_enabled"))
