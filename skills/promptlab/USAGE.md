# PromptLab 使用说明

## 自动触发
对话里出现以下词就会自动匹配：提示词、即梦、Seedream、概念图、角色三视图、绘本分镜、影视分镜、运镜、镜头语言、动效卡点、跨页一致。

## 手动调用
直接说"用 promptlab 技能"。技能名就是 `promptlab`，已在全局技能列表中，无需再注册。

## 跑自检脚本
先进入技能目录（任意位置 `cd` 过去即可），用相对路径跑：

```bash
cd ~/.trae-cn/skills/promptlab
python scripts/check_prompt.py -p "你的提示词"
python scripts/check_prompt.py -f prompt.txt
python scripts/check_prompt.py -b prompts.txt
python scripts/check_prompt.py --lang en -p "prompt"
```

也可进入 `scripts` 目录后直接 `python check_prompt.py -p "..."`。

- 依赖：Python 3.8+，只用标准库，不读任何外部数据文件。
- 退出码 `0` = 全部可提交；`1` = 批量结果里有需修改项，不是崩溃。

## 生效时机
技能在**新建对话**时扫描加载。改了 `SKILL.md` 或 `references/` 后，开一个新对话才生效，旧对话仍用旧内容。

## 维护
只改本目录内文件。不要在项目目录或其他位置复制副本，否则会出现同名技能冲突。
