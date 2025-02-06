from ...env import ENVS

LIB_PATH = ENVS.bot.word_lib


with open(LIB_PATH, encoding="utf-8") as fp:
    alist = fp.readlines()
amap = map(lambda x: x.rstrip("\n").split("##"), alist)
adict: dict[str, list[str]] = {}
for k, v in amap:
    dict_val = adict.get(k)
    if dict_val is None:
        adict[k] = [v]
    else:
        dict_val.append(v)


def save_dict() -> None:
    with open(LIB_PATH, "w", encoding="utf-8") as f:
        for key, vals in WORD_DICT.items():
            for val in vals:
                f.write(f"{key}##{val}\n")


def add_pair(ask: str, ans: str) -> bool:
    ans_arr = WORD_DICT.get(ask)
    if ans_arr is None:
        WORD_DICT[ask] = [ans]
        save_dict()
        return True
    if ans not in ans_arr:
        ans_arr.append(ans)
        save_dict()
        return True
    return False


WORD_DICT = adict
BOT_FLAG = "$$bot$$"
SENDER_FLAG = "$$sender$$"
OWNER_FLAG = "$$owner$$"
