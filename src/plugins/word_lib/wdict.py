from ...env import ENVS

WORDS_FILES = ENVS.bot.word_lib


def load_dict() -> dict[str, list[str]]:
    wdict: dict[str, list[str]] = {}
    for file in WORDS_FILES:
        with open(file, encoding="utf-8") as fp:
            alist = fp.readlines()
        wmap = map(lambda x: x.rstrip("\n").split("##"), alist)
        for k, v in wmap:
            wdict.setdefault(k, []).append(v)
    return wdict


def _save_dict() -> None:
    assert len(WORDS_FILES), "没有可用的词库文件，因此拒绝添加条目"
    with open(WORDS_FILES[0], "w", encoding="utf-8") as fp:
        for key, vals in WORDS_DICT.items():
            for val in vals:
                fp.write(f"{key}##{val}\n")


def add_pair(ask: str, ans: str) -> bool:
    ans_arr = WORDS_DICT.get(ask)
    if ans_arr is None:
        WORDS_DICT[ask] = [ans]
        _save_dict()
        return True
    if ans not in ans_arr:
        ans_arr.append(ans)
        _save_dict()
        return True
    return False


WORDS_DICT = load_dict()
BOT_FLAG = "$$bot$$"
SENDER_FLAG = "$$sender$$"
OWNER_FLAG = "$$owner$$"
