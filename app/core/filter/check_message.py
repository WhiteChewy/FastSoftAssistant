import re

from aiogram.filters import BaseFilter
from aiogram.types import Message


class CheckMessage(BaseFilter):

    async def __call__(self, message: Message) -> object or None:
        self.message = message
        return self.check_message()

    def check_message(self) -> bool:
        ping_re = re.compile(r'(слыш)ь*(,)* *бай(,)* посчитай(те)*|ув(а|о)жаемы(й|е)(,)* *бай *(по|рас)считай(те)*')
        return self.message.caption and re.search(ping_re, self.message.caption.lower())
