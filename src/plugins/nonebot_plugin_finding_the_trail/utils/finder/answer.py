#  Moonlark - A new ChatBot
#  Copyright (C) 2024  Moonlark Development Team
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ##############################################################################

import copy

from src.plugins.nonebot_plugin_finding_the_trail.utils.enums.blocks import Blocks
from src.plugins.nonebot_plugin_finding_the_trail.utils.enums.directions import Directions
from src.plugins.nonebot_plugin_finding_the_trail.utils.finder.utils import get_moveable_directions, NodeData, \
    MovementExecutor, get_back_direction


class AnswerFinder:

    def __init__(self, game_map: list[list[Blocks]]) -> None:
        self.game_map = game_map
        self.answer = []

    def get_start_pos(self) -> list[int]:
        for row in range(len(self.game_map)):
            for col in range(len(self.game_map[row])):
                if self.game_map[row][col] == Blocks.START:
                    return [row, col]

    def init_stack(self) -> list[NodeData]:
        start_pos = self.get_start_pos()
        return [{
            "game_map": copy.deepcopy(self.game_map),
            "pos": start_pos,
            "answer": [d]
        } for d in get_moveable_directions(start_pos, self.game_map, [])]

    def search(self) -> list[Directions]:
        stack = self.init_stack()
        while len(stack) > 0:
            node = stack.pop(0)
            executor = MovementExecutor(node["game_map"], node["pos"], node["answer"][-1])
            pos = executor.get_moved_pos()
            game_map = executor.get_game_map()
            if game_map[pos[0]][pos[1]] == Blocks.END:
                self.answer = node["answer"]
                return self.answer
            if executor.is_map_changed():
                d_ignore = []
            else:
                d_ignore = [get_back_direction(node["answer"][-1])]
            for d in get_moveable_directions(pos, game_map, d_ignore):
                stack.append({
                    "game_map": game_map,
                    "pos": pos,
                    "answer": node["answer"] + [d]
                })
        return []
