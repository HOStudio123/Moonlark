import traceback
from nonebot.matcher import Matcher
from types import ModuleType
from sqlalchemy.exc import NoResultFound
import random
import inspect
from nonebot import get_plugin_by_module_name, logger
from nonebot_plugin_orm import get_session
from .model import LanguageData, LanguageKey
from .model import LanguageConfig
from .exception import *
from nonebot import get_plugin_config
from .config import Config
from .loader import LangLoader
from pathlib import Path
from nonebot import get_driver

languages = {}
config = get_plugin_config(Config)

@get_driver().on_startup
async def load_languages() -> None:
    global languages
    loader = LangLoader(Path(config.language_dir))
    await loader.init()
    await loader.load()
    languages = loader.get_languages().copy()

def get_module_name(module: ModuleType | None) -> str | None:
    if module is None:
        return
    if (plugin := get_plugin_by_module_name(module.__name__)) is None:
        return
    return plugin.name[15:] if plugin.name.startswith("nonebot_plugin_") else plugin.name

def get_key(language: str, plugin: str, key: list[str]) -> LanguageKey:
    data = languages[language].keys[plugin]
    try:
        for k in key:
            data = data[k]
    except KeyError:
        raise InvalidKeyException(f"{plugin}::{key}")
    if not isinstance(data, LanguageKey):
        raise InvalidKeyException(f"{plugin}::{key}")
    return data

def apply_template(language: str, plugin: str, key: list[str], text: str) -> str:
    try:
        return random.choice(get_key(
            language,
            plugin,
            key[:-1] + ["__template__"]
        ).text).format(text)
    except InvalidKeyException:
        return text

def get_text(language: str, plugin: str, key: str, *args, **kwargs) -> str:
    k = key.split(".")
    try:
        data = get_key(
            language,
            plugin,
            k
        )
    except InvalidKeyException:
        text = f"<缺失: {plugin}.{key}; {args}; {kwargs}>"
        logger.warning(f"获取键失败: {traceback.format_exc()}")
    else:
        text = random.choice(data.text)
        if data.use_template:
            text = apply_template(
                language,
                plugin,
                k,
                text
            )
    return text.format(
        *args,
        **kwargs,
        __prefix__=config.command_start[0]
    )

def get_languages() -> dict[str, LanguageData]:
    return languages

async def set_user_language(user_id: str, language: str) -> None:
    session = get_session()
    try:
        data = await session.get_one(
            LanguageConfig,
            {
                "user_id": user_id
            }
        )
        data.language = language
    except NoResultFound:
        session.add(LanguageConfig(
            user_id=user_id,
            language=language
        ))
    await session.commit()

async def get_user_language(user_id: str) -> str:
    session = get_session()
    try:
        language = await session.get_one(
            LanguageConfig, 
            {"user_id": user_id}
        )
    except NoResultFound:
        language = config.language_index_order[0]
    if language not in languages:
        await set_user_language(
            user_id,
            language := config.language_index_order[0]
        )
    return language


class LangHelper:

    def __init__(self, name: str = "") -> None:
        module = inspect.getmodule(inspect.stack()[1][0])
        self.plugin_name = name or get_module_name(module) or ""
        if not self.plugin_name:
            raise InvalidPluginNameException(self.plugin_name)
        
    
    async def text(self, key: str, user_id: str | int, *args, **kwargs) -> str:
        language = await get_user_language(str(user_id))
        return get_text(
            language,
            self.plugin_name,
            key,
            *args,
            **kwargs
        )

    async def send(
            self,
            key: str,
            user_id: str | int,
            *args,
            matcher: Matcher = Matcher(),
            at_sender: bool = True,
            reply_message: bool = False,
            **kwargs) -> None:
        await matcher.send(await self.text(
            key,
            user_id,
            *args,
            **kwargs
        ), at_sender=at_sender, reply_message=reply_message)

    async def reply(
            self,
            key: str,
            user_id: str | int,
            *args,
            **kwargs) -> None:
        await self.send(
            key,
            user_id,
            *args,
            **kwargs,
            at_sender=False,
            reply_message=True
        )
