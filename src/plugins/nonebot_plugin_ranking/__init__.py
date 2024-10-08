from nonebot import require
from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_ranking",
    description="",
    usage="",
)

require("nonebot_plugin_larklang")
require("nonebot_plugin_larkuser")
require("nonebot_plugin_larkuid")
require("nonebot_plugin_render")
require("nonebot_plugin_larkutils")

from .generator import generate_image
from .web import WebRanking, register
from .types import *
