from telethon import events, functions, types
from telethon.tl.types import UserStatusOnline, UserStatusOffline
from hikkatl.types import Message
from .. import loader, utils

@loader.tds
class OnlineMonitorMod(loader.Module):
    """Monitors online status of a user"""
    strings = {"name": "OnlineMonitorMod", "user_tag": "Monitoring user: {}"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "user_id",
                None,
                "ID of the user to monitor",
                validator=loader.validators.TelegramID(),
            ),
        )
        self._chat_id = 7081811526

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._me = await client.get_me()

        # Create a new group for logging
        result = await client(functions.messages.CreateChatRequest(
            users=[self._me.id],
            title="Online Status Logs"
        ))
        self._chat_id = result.chats[0].id

        # Add the event handler
        self._client.add_event_handler(self.on_new_message, events.UserUpdate(chats=None, from_users=self.config["user_id"]))

    async def on_new_message(self, event):
        if isinstance(event.status, UserStatusOnline):
            await self._client.send_message(self._chat_id, f"User {self.config['user_id']} is now online")
        elif isinstance(event.status, UserStatusOffline):
            await self._client.send_message(self._chat_id, f"User {self.config['user_id']} is now offline")

    @loader.command(
        ru_doc="Устанавливает ID пользователя для мониторинга",
    )
    async def setuser(self, message: Message):
        """Sets the user ID to monitor"""
        args = utils.get_args(message)
        if not args:
            return await utils.answer(message, "Please provide a user ID")
        
        try:
            user_id = int(args[0])
        except ValueError:
            return await utils.answer(message, "Invalid user ID")
        
        self.config["user_id"] = user_id
        await utils.answer(message, self.strings("user_tag").format(user_id))
