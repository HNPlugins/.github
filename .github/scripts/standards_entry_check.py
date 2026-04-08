#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_FILES = ("AGENTS.md", "CONTRIBUTING.md")
WIKI_PATTERNS = (
    r"HNProjects/Wiki",
    r"HNPlugins/Wiki",
    r"HNWiki",
)
CORE_PATTERNS = (
    r"HNCore",
    r"HNCoreAPI",
    r"hncore-api",
)
CORE_REUSE_PATTERNS = (
    r"复用",
    r"扩展",
    r"沉淀",
    r"重复造轮子",
    r"公共模块",
    r"公共能力",
)
SELFCHECK_PATTERNS = (
    r"自检",
    r"提交前",
    r"团队规范",
    r"组织规范",
)


def has_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def check_wiki(text: str) -> bool:
    return has_any(text, WIKI_PATTERNS)


def check_core_reuse(text: str) -> bool:
    return has_any(text, CORE_PATTERNS) and has_any(text, CORE_REUSE_PATTERNS)


def check_selfcheck(text: str) -> bool:
    return has_any(text, SELFCHECK_PATTERNS)


SIGNALS = (
    (
        "Wiki 文档入口",
        check_wiki,
        "请补充“用户向内容统一以 HNProjects/Wiki 为准”之类说明。",
    ),
    (
        "HNCore 优先复用提示",
        check_core_reuse,
        "请补充“当前在开发 HNCore 下游仓库时，应优先复用 HNCore / HNCoreAPI / 组织公共能力”之类说明。",
    ),
    (
        "提交前自检要求",
        check_selfcheck,
        "请补充“提交前必须按组织规范与仓库规范完成自检”之类说明。",
    ),
)


def report_error(file_name: str, message: str) -> None:
    escaped = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    print(f"::error file={file_name}::{escaped}")



def main() -> int:
    parser = argparse.ArgumentParser(description="检查仓库入口文档是否符合团队规范。")
    parser.add_argument("repo_path", help="要检查的仓库路径")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    repo_name = repo_path.name

    if not repo_path.exists() or not repo_path.is_dir():
        print(f"[FAIL] 仓库路径不存在或不是目录：{repo_path}")
        return 2

    errors: list[str] = []

    for file_name in REQUIRED_FILES:
        file_path = repo_path / file_name
        if not file_path.is_file():
            message = (
                f"缺少根目录文件 `{file_name}`。请新增该入口文档，并补齐 Wiki 文档入口、"
                "HNCore 优先复用提示与提交前自检要求。"
            )
            report_error(file_name, message)
            errors.append(message)
            continue

        text = file_path.read_text(encoding="utf-8")
        for label, checker, guidance in SIGNALS:
            if checker(text):
                continue
            message = f"`{file_name}` 缺少“{label}”。{guidance}"
            report_error(file_name, message)
            errors.append(message)

    if errors:
        print(f"\n[FAIL] {repo_name} 未通过仓库入口规范检查。")
        print("请至少确认以下几点：")
        print("- 根目录存在 AGENTS.md 与 CONTRIBUTING.md")
        print("- 文档明确指向 HNProjects/Wiki 作为用户向内容正式落点")
        print("- 文档明确提示优先复用 HNCore / HNCoreAPI / 组织公共能力")
        print("- 文档明确要求提交前按组织规范与仓库规范完成自检")
        print("提示：当前在开发 HNCore 下游仓库时，应优先复用 HNCore / HNCoreAPI / 组织公共能力。")
        return 1

    print(f"[PASS] {repo_name} 已通过仓库入口规范检查。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
