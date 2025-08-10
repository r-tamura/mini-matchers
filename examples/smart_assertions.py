"""
スマートアサーション機能のデモ

mini-matchersライブラリを使用した実用的な使用例を示します。
通常のassert文でマッチャーオブジェクトを使用できる機能のデモンストレーションです。
"""

import sys
import os
from datetime import datetime, timedelta
import pytest

# パッケージのパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# mini-matchersライブラリから必要な機能をインポート
from mini_matchers import regex, around_now, greater_than, less_than, any_of, contains


# 使用例とテスト
def myfunc():
    """テスト対象の関数（例）"""
    return {
        "prop1": 42,
        "random_id": "1234567890",
        "prop_date": datetime.now(),
        "prop_date2": datetime.now() - timedelta(seconds=30),
        "status": "success",
        "count": 15,
        "message": "Hello World"
    }


def test_smart_assertions_basic():
    """基本的なスマートアサーションのテスト"""
    actual = myfunc()
    
    # 理想的な使用方法
    expected = {
        "prop1": 42,
        "random_id": regex(r"[0-9]{10}"),
        "prop_date": around_now(),
        "prop_date2": around_now(300),  # 前後5分以内ならOK
        "status": any_of("success", "completed", "done"),
        "count": greater_than(10),
        "message": contains("Hello")
    }
    
    # 通常のassert文で比較
    assert actual == expected


def test_smart_assertions_individual():
    """個別のマッチャーテスト"""
    actual = myfunc()
    
    # 個別にテスト
    assert actual["random_id"] == regex(r"[0-9]{10}")
    assert actual["prop_date"] == around_now()
    assert actual["prop_date2"] == around_now(300)
    assert actual["status"] == any_of("success", "completed")
    assert actual["count"] == greater_than(10)
    assert actual["message"] == contains("Hello")


def test_smart_assertions_failure_cases():
    """失敗ケースのテスト"""
    actual = myfunc()
    
    # 失敗するケース
    with pytest.raises(AssertionError):
        assert actual == {
            "prop1": 42,
            "random_id": regex(r"[a-z]{10}"),  # 数字のはずが文字を期待
            "prop_date": around_now(),
            "prop_date2": around_now(300),
            "status": "success",
            "count": greater_than(10),
            "message": contains("Hello")
        }


def test_nested_smart_assertions():
    """ネストされた構造でのスマートアサーション"""
    def complex_func():
        return {
            "user": {
                "id": 12345,
                "name": "Alice",
                "email": "alice@example.com",
                "created_at": datetime.now()
            },
            "metadata": {
                "version": "1.2.3",
                "build_id": "abc123def456",
                "timestamp": datetime.now() - timedelta(minutes=1)
            }
        }
    
    actual = complex_func()
    
    expected = {
        "user": {
            "id": greater_than(10000),
            "name": any_of("Alice", "Bob", "Charlie"),
            "email": regex(r"^[\w\.-]+@[\w\.-]+\.\w+$"),
            "created_at": around_now()
        },
        "metadata": {
            "version": regex(r"\d+\.\d+\.\d+"),
            "build_id": regex(r"[a-f0-9]{12}"),
            "timestamp": around_now(120)  # 2分以内
        }
    }
    
    assert actual == expected


def test_list_with_smart_matchers():
    """リスト内でのスマートマッチャー使用"""
    def list_func():
        return [
            {"id": 1, "name": "Item 1", "created": datetime.now()},
            {"id": 2, "name": "Item 2", "created": datetime.now() - timedelta(seconds=10)},
            {"id": 3, "name": "Item 3", "created": datetime.now() - timedelta(seconds=20)}
        ]
    
    actual = list_func()
    
    # リストの各要素をスマートマッチャーで検証
    expected = [
        {"id": 1, "name": contains("Item"), "created": around_now()},
        {"id": 2, "name": contains("Item"), "created": around_now()},
        {"id": 3, "name": contains("Item"), "created": around_now()}
    ]
    
    assert actual == expected


# 高度な使用例
class APIResponse:
    """API レスポンスのモック"""
    
    @staticmethod
    def get_user(user_id: int):
        return {
            "id": user_id,
            "username": f"user_{user_id}",
            "email": f"user_{user_id}@example.com",
            "profile": {
                "full_name": "Test User",
                "bio": "This is a test user profile",
                "avatar_url": f"https://example.com/avatars/{user_id}.jpg",
                "follower_count": 42,
                "following_count": 15
            },
            "settings": {
                "theme": "dark",
                "notifications": True,
                "privacy": "public"
            },
            "created_at": "2024-01-15T10:30:00Z",
            "last_login": datetime.now().isoformat(),
            "is_verified": True
        }


def test_api_response_validation():
    """API レスポンスの検証例"""
    user_id = 123
    response = APIResponse.get_user(user_id)
    
    expected_response = {
        "id": user_id,
        "username": regex(r"user_\d+"),
        "email": regex(r"user_\d+@example\.com"),
        "profile": {
            "full_name": contains("User"),
            "bio": contains("test"),
            "avatar_url": regex(r"https://example\.com/avatars/\d+\.jpg"),
            "follower_count": greater_than(0),
            "following_count": greater_than(0)
        },
        "settings": {
            "theme": any_of("light", "dark", "auto"),
            "notifications": any_of(True, False),
            "privacy": any_of("public", "private", "friends")
        },
        "created_at": regex(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"),
        "last_login": regex(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
        "is_verified": any_of(True, False)
    }
    
    assert response == expected_response


if __name__ == "__main__":
    print("=== スマートアサーション機能のデモ ===")
    
    tests = [
        ("基本的なスマートアサーション", test_smart_assertions_basic),
        ("個別マッチャーテスト", test_smart_assertions_individual),
        ("ネストされた構造", test_nested_smart_assertions),
        ("リスト内マッチャー", test_list_with_smart_matchers),
        ("API レスポンス検証", test_api_response_validation),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✓ {test_name}: 成功")
        except Exception as e:
            print(f"✗ {test_name}: 失敗 - {e}")
    
    print("\n=== 使用例 ===")
    print("def test_mytest():")
    print("    actual = myfunc()")
    print("    assert actual == {")
    print("        'prop1': 42,")
    print("        'random_id': regex('[0-9]{10}'),")
    print("        'prop_date': around_now(),")
    print("        'prop_date2': around_now(300)  # 前後5分以内ならOK")
    print("    }")
    
    print("\n全てのテストを実行するには: pytest examples/smart_assertions.py -v")