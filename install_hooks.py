#!/usr/bin/env python3
"""
Claude Code Hooks 설치 스크립트

이 스크립트는 Claude Code의 settings.json에 hook 설정을 추가합니다.
"""
import json
import os
import sys
import argparse
from pathlib import Path


def get_hooks_path():
    """Hook 스크립트 경로 반환"""
    return Path(__file__).parent / "src" / "hooks"


def get_claude_settings_path(scope: str) -> Path:
    """Claude 설정 파일 경로 반환"""
    if scope == "user":
        return Path.home() / ".claude" / "settings.json"
    elif scope == "project":
        return Path.cwd() / ".claude" / "settings.json"
    else:
        raise ValueError(f"Unknown scope: {scope}")


def load_settings(settings_path: Path) -> dict:
    """기존 설정 로드"""
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(settings_path: Path, settings: dict):
    """설정 저장"""
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def create_hooks_config(hooks_path: Path) -> dict:
    """Hooks 설정 생성"""
    notify_hook = str(hooks_path / "notify_hook.py")
    stop_hook = str(hooks_path / "stop_hook.py")

    return {
        "Notification": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": f'python3 "{notify_hook}"'
                    }
                ]
            }
        ],
        "Stop": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": f'python3 "{stop_hook}"'
                    }
                ]
            }
        ]
    }


def install_hooks(scope: str, force: bool = False):
    """Hooks 설치"""
    hooks_path = get_hooks_path()
    settings_path = get_claude_settings_path(scope)

    print(f"Hook 스크립트 경로: {hooks_path}")
    print(f"설정 파일 경로: {settings_path}")

    # 기존 설정 로드
    settings = load_settings(settings_path)

    # hooks 키가 이미 있는 경우
    if "hooks" in settings and not force:
        print("\n⚠️  기존 hooks 설정이 있습니다.")
        print("덮어쓰려면 --force 옵션을 사용하세요.")
        print("\n현재 hooks 설정:")
        print(json.dumps(settings["hooks"], indent=2, ensure_ascii=False))
        return False

    # 새 hooks 설정 추가
    settings["hooks"] = create_hooks_config(hooks_path)

    # 저장
    save_settings(settings_path, settings)

    print("\n✅ Hooks 설정이 설치되었습니다!")
    print(f"\n설정 파일: {settings_path}")
    print("\n설치된 hooks:")
    print("  - Notification: 알림 이벤트 (idle_prompt, permission_prompt 등)")
    print("  - Stop: 작업 완료 이벤트")
    print("\n[다음 단계]")
    print("1. Claude Code Notifier 트레이 앱 실행:")
    print("   python src/main.py")
    print("\n2. Claude Code 사용 시 자동으로 알림이 표시됩니다.")
    return True


def uninstall_hooks(scope: str):
    """Hooks 제거"""
    settings_path = get_claude_settings_path(scope)

    if not settings_path.exists():
        print("설정 파일이 없습니다.")
        return False

    settings = load_settings(settings_path)

    if "hooks" not in settings:
        print("hooks 설정이 없습니다.")
        return False

    del settings["hooks"]
    save_settings(settings_path, settings)

    print("✅ Hooks 설정이 제거되었습니다.")
    return True


def show_status(scope: str):
    """현재 hooks 상태 표시"""
    settings_path = get_claude_settings_path(scope)

    print(f"설정 파일: {settings_path}")

    if not settings_path.exists():
        print("상태: 설정 파일 없음")
        return

    settings = load_settings(settings_path)

    if "hooks" not in settings:
        print("상태: hooks 설정 없음")
        return

    print("상태: hooks 설정됨")
    print("\n현재 hooks 설정:")
    print(json.dumps(settings["hooks"], indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code Notifier Hooks 설치/관리"
    )
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "status"],
        help="수행할 작업"
    )
    parser.add_argument(
        "--scope",
        choices=["user", "project"],
        default="user",
        help="설정 범위 (user: ~/.claude, project: ./.claude)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="기존 설정 덮어쓰기"
    )

    args = parser.parse_args()

    if args.action == "install":
        install_hooks(args.scope, args.force)
    elif args.action == "uninstall":
        uninstall_hooks(args.scope)
    elif args.action == "status":
        show_status(args.scope)


if __name__ == "__main__":
    main()
