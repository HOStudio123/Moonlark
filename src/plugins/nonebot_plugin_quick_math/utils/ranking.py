from ...nonebot_plugin_ranking.web import WebRanking
from ...nonebot_plugin_ranking.types import RankingData
from ..models import QuickMathUser
from ..__main__ import lang

from nonebot_plugin_orm import get_session
from sqlalchemy import select
from typing import Any, AsyncGenerator


async def get_user_list(order_by: Any = QuickMathUser.max_point) -> AsyncGenerator[QuickMathUser, None]:
    async with get_session() as session:
        data = await session.scalars(select(QuickMathUser).order_by(order_by.desc()))
        for user in data:
            yield user


class RecordRanking(WebRanking):
    ID = "quick_math_record"
    NAME = "rank.title-1"
    LANG = lang

    async def get_sorted_data(self) -> list[RankingData]:
        return [
            {
                "user_id": user.user_id,
                "data": user.max_point,
                "info": None,
            }
            async for user in get_user_list()
        ]


class TotalRanking(WebRanking):
    ID = "quick_math_total"
    NAME = "rank.title-2"
    LANG = lang

    async def get_sorted_data(self) -> list[RankingData]:
        return [
            {
                "user_id": user.user_id,
                "data": user.total_point,
                "info": None,
            }
            async for user in get_user_list(QuickMathUser.total_point)
        ]


web_ranking = [RecordRanking(), TotalRanking()]
