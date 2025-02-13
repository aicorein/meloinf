import os


def main() -> None:
    ret = os.system("pdm export -o requirements.txt --without dev")
    if ret == 0:
        print("已刷新项目的 requirements.txt")
    else:
        print("未能完成刷新项目的 requirements.txt 的任务")
