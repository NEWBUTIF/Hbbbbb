from hikkatl.types import Message
from .. import loader

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
    }

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
            self.config["user_id"] = user.id
            await utils.answer(message, self.strings("user_set_by_username").format(f"{username} ({note})"))
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
            self.config["user_id"] = user_id
            await utils.answer(message, self.strings("user_set_by_id").format(f"{user_id} ({note})"))
        except ValueError:
            await utils.answer(message, self.strings("invalid_user_id"))
