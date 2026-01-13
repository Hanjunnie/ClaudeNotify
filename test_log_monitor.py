#!/usr/bin/env python3
"""
로그 모니터링 테스트 스크립트
테스트 로그 파일에 내용을 쓰고 감지되는지 확인
"""
import time
import os
from pathlib import Path

def create_test_log():
    """테스트 로그 파일 생성"""
    test_dir = Path("/tmp/claude_test")
    test_dir.mkdir(exist_ok=True)

    test_log = test_dir / "test.log"

    print(f"테스트 로그 파일 생성: {test_log}")
    print("다음 명령어로 프로그램을 실행하세요:")
    print(f"  python main.py --log-path {test_log}")
    print()
    print("엔터를 누르면 테스트 메시지를 작성합니다...")
    input()

    # 테스트 메시지 작성
    test_messages = [
        "Yes 응답 테스트",
        "작업이 completed 되었습니다",
        "Successfully 완료",
        "AskUserQuestion이 호출되었습니다",
        "다음 중 선택하세요",
    ]

    with open(test_log, 'a') as f:
        for i, msg in enumerate(test_messages, 1):
            print(f"{i}. 메시지 작성: {msg}")
            f.write(f"{msg}\n")
            f.flush()
            time.sleep(2)  # 2초 간격으로 작성

    print("\n모든 테스트 메시지를 작성했습니다!")
    print("알림이 표시되었나요?")

if __name__ == "__main__":
    create_test_log()
