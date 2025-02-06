import json
import os
import random
import re
import tomllib
from typing import Dict, List, Optional

from ...env import ENVS
from .. import code_compile

R_REGEX = re.compile(r"(\d*d\d*)")


def _convert_r_exp(string: str) -> str:
    ns = string.lower().replace("x", "*")
    ss = R_REGEX.split(ns)

    for i in range(1, len(ss), 2):
        a, b = ss[i].split("d")
        if a == "" and b == "":
            a, b = ENVS.bot.dice_base_r
        else:
            a, b = int(a), int(b)

        res = 0
        for _ in range(a):
            res += random.randint(1, b)
        ss[i] = str(res)

    return "".join(ss)


def r_gen(string: str) -> str:
    try:
        exp = _convert_r_exp(string)
        return str(eval(exp))  # pylint: disable=eval-used

    except Exception as e:
        return f"掷骰表达式无法解析：\n[{e.__class__.__name__}] {e}"


async def safe_r_gen(string: str) -> str:
    try:
        exp = _convert_r_exp(string)
        output, exc = await code_compile.calc_exp(exp)
        if exc:
            raise exc
        return output

    except Exception as e:
        return f"掷骰表达式无法解析：\n[{e.__class__.__name__}] {e}"


class DeckItem:

    class DrawRecords:
        def __init__(
            self, deck_name: str, sample_num: int, replace: bool, pos: List[int]
        ) -> None:
            self.deck_name = deck_name
            self.sample_num = sample_num
            self.replace = replace
            self.pos = pos
            self.res: list[str]

    def __init__(self, raw: str, group_name: str) -> None:
        self._deck_regex = re.compile(r"\{(.+?)\}")
        self._var_regex = re.compile(r"\[(.+?)\]")
        self._freq_regex = re.compile(r"^::(\d+)::")

        res = self._freq_regex.search(raw)
        self.freq = int(res.group(1)) if res is not None else 1
        self.exp = self._freq_regex.sub("", raw)
        self.namespace = group_name

    def format(self) -> str:
        ss = self._var_regex.split(self.exp)
        for i in range(1, len(ss), 2):
            ss[i] = r_gen(ss[i])
        join_ss = "".join(ss)

        ss = self._deck_regex.split(join_ss)
        draw_recs: Dict[str, DeckItem.DrawRecords] = {}
        for i in range(1, len(ss), 2):
            replace = True
            if ss[i][0] == "%":
                replace = False
                ss[i] = ss[i][1:]
            rec = draw_recs.get(ss[i])

            if rec is None:
                rec = DeckItem.DrawRecords(ss[i], 1, replace, [i])
                draw_recs[ss[i]] = rec
            else:
                rec.sample_num += 1
                rec.pos.append(i)
                if not replace:
                    rec.replace = False

        for rec in draw_recs.values():
            cur_group = DeckStore.get(self.namespace)
            if cur_group is None:
                raise ValueError(
                    f"在格式化牌堆项目时，遇到了不存在的牌堆组，尝试获取的牌堆组：{self.namespace}"
                )
            deck = cur_group.decks[rec.deck_name]
            rec.res = deck.draw(rec.sample_num, rec.replace)

        for rec in draw_recs.values():
            for i, j in enumerate(rec.pos):
                ss[j] = rec.res[i]

        return "".join(ss)


class Deck:
    def __init__(self, name: str, items: List[DeckItem]) -> None:
        self._items = items
        self.name = name
        self.freqs = [item.freq for item in items]
        self.count = len(items)

    def draw(self, sample_num: int = 1, replace: bool = False) -> List[str]:
        if replace:
            samples = random.choices(self._items, self.freqs, k=sample_num)
        else:
            samples = random.sample(self._items, sample_num, counts=self.freqs)
        ss = [sample.format() for sample in samples]
        return ss


class DeckGroup:
    def __init__(self, name: str, cmds: List[str]) -> None:
        self.decks: Dict[str, Deck] = {}
        self.name = name
        self.cmds = cmds

    def add(self, name: str, deck: Deck) -> None:
        res = self.decks.get(name)
        if res is not None:
            raise ValueError(f"名为 {name} 的牌堆已存在，请更改牌堆名以避免重名")
        self.decks[name] = deck

    def get_count(self) -> int:
        return sum({deck.count for deck in self.decks.values()})


class DeckStore:
    __store__: Dict[str, DeckGroup] = {}

    @classmethod
    def get(cls, group_name: str) -> Optional[DeckGroup]:
        return cls.__store__.get(group_name)

    @classmethod
    def get_all(cls) -> Dict[str, DeckGroup]:
        return cls.__store__

    @classmethod
    def get_count(cls) -> int:
        return sum({group.get_count() for group in cls.__store__.values()})

    @classmethod
    def add(cls, group_name: str, group: DeckGroup) -> None:
        res = cls.__store__.get(group_name)
        if res is not None:
            raise ValueError(
                f"名为 {group_name} 的牌堆组已存在，请更改对应文件名以避免重名"
            )
        cls.__store__[group_name] = group

    @classmethod
    def build(cls) -> None:
        deck_dir = ENVS.bot.dice_data_dir
        with open(ENVS.bot.dice_config, "rb") as fp:
            cmd_map = tomllib.load(fp)

        for filename, cmds in cmd_map.items():
            with open(os.path.join(deck_dir, filename + ".json"), encoding="utf-8") as fp:
                deck_json = json.load(fp)

            for cmd in cmds:
                if cmd not in deck_json.keys():
                    raise ValueError(f"牌堆文件 {filename} 中不存在名为 {cmd} 的触发牌堆")

            deck_group = DeckGroup(filename, cmds)
            cls.add(filename, deck_group)

            for deck_name, deck_raw in deck_json.items():
                deck_items = [DeckItem(item, filename) for item in deck_raw]
                deck = Deck(deck_name, deck_items)
                deck_group.add(deck_name, deck)


DeckStore.build()
