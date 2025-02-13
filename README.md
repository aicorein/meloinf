<div align="center">
  <img width=256 src="https://github.com/Meloland/melobot/blob/main/docs/source/_static/logo.png?raw=true" />
  <h1>meloinf</h1>
  <p>
    <strong>一个简简单单的 bot，基于 melobot</strong>
  </p>
  <p align="center">
    <a href="https://github.com/aicorein/meloinf/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-AGPL3-2ea44f" alt="license - BSD-3-Clause"></a>
    <a href="https://python.org" title="Go to Python homepage"><img src="https://img.shields.io/badge/Python-3.13%20%7C%203.14-2ea44f?logo=python&logoColor=white" alt="Made with Python"></a>
    <a href="https://github.com/aicorein/meloinf"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/aicorein/meloinf"></a>
  </p>
  <p>
    <a href="https://pdm-project.org"><img src="https://img.shields.io/badge/PDM-Managed-purple?logo=pdm&logoColor=white" alt="PDM - Managed"></a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
    <a href="https://mypy-lang.org/"><img src="https://www.mypy-lang.org/static/mypy_badge.svg" alt="Checked with mypy"></a>
  </p>
</div>

## 💬 简介

基于 [melobot](https://github.com/aicorein/melobot) 的机器人项目。现在仍在开发中。

目前暂时支持通过 onebot v11 协议提供服务，未来将会扩展为各平台的通用机器人。

## 📦️ 配置使用

1. clone 本项目

```shell
git clone https://github.com/aicorein/meloinf.git
```

2. 重命名 `src/env.toml.bak` 为 `src/env.toml` 以启用配置文件，同时自行修改配置

3. 在 `>=3.13` 的 python 环境中安装依赖项：

```shell
pip install ./requirements.txt
```

4. 运行

```shell
cd src
python -m melobot run main.py
```

## 📜 开源许可

本项目在 `AGPL3` 协议下开源发行。

此外，本项目借鉴或修改了来自以下项目的代码、数据文件。所有原始的 LICENSE 文件已保留，本项目的许可证也与以下项目兼容。

| 对应项目                                                     | 本项目中对应的 LICENSE                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Giftia/Project_Xiaoye](https://github.com/Giftia/Project_Xiaoye) | [./src/data/wordlib/LICENSE-GPL](./src/data/wordlib/LICENSE-GPL) |
| [menzi11/BullshitGenerator](https://github.com/menzi11/BullshitGenerator) | [./src/plugins/bullshit_gen/LICENSE](./src/plugins/bullshit_gen/LICENSE) |
| [RMYHY/RBot](https://github.com/RMYHY/RBot)                  | [./src/plugins/asoul_illness/LICENSE](./src/plugins/asoul_illness/LICENSE) |
| [Kyomotoi/AnimeThesaurus](https://github.com/Kyomotoi/AnimeThesaurus) | [./src/data/wordlib/LICENSE-MIT](./src/data/wordlib/LICENSE-MIT) |

> 衷心感谢你们为开源社区做出的贡献 ✨
