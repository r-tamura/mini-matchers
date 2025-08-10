# mini-matchers

通常の`assert`文でマッチャーオブジェクトを使用できる軽量Pythonライブラリです。動的な値や複雑なデータ構造を含むテストを簡潔に記述できます。

## 特徴

- 🎯 **シンプル**: 通常の`assert`文をそのまま使用
- 🔧 **柔軟**: 正規表現、時刻範囲、数値比較など豊富なマッチャー
- 🛡️ **型安全**: 完全な型ヒント対応
- 🔧 **拡張可能**: 独自のマッチャーを簡単に作成可能
- 📝 **明確**: テスト失敗時に分かりやすいメッセージを表示

## インストール

```bash
pip install mini-matchers
```

## 基本的な使い方

通常の`assert`文でマッチャーオブジェクトを使用できます：

```python
from mini_matchers import regex, around_now, greater_than, any_of, contains
from datetime import datetime

def test_mytest():
    actual = myfunc()
    assert actual == {
        "prop1": 42,
        "random_id": regex(r"[0-9]{10}"),
        "prop_date": around_now(),
        "prop_date2": around_now(300),  # 前後5分以内ならOK
        "status": any_of("success", "completed", "done"),
        "message": contains("Hello")
    }
```

### 数値の比較

```python
def test_numeric_matching():
    assert 10 == greater_than(5)
    assert 3 == less_than(10)
    assert 5.5 == greater_than(5.0)
```

### 文字列のマッチング

```python
def test_string_matching():
    assert "hello world" == contains("world")
    assert "test@example.com" == regex(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    assert "success" == any_of("success", "completed", "done")
```

### 時刻の検証

```python
def test_time_matching():
    from datetime import datetime
    
    assert datetime.now() == around_now()  # デフォルト60秒以内
    assert datetime.now() == around_now(300)  # 5分以内
```

## カスタムマッチャーの作成

独自のマッチャーを作成することができます：

```python
from mini_matchers import BaseMatcherMixin, SmartMatcher
from typing import Any

class ToBeEvenMatcher(BaseMatcherMixin):
    """偶数かどうかをチェックするマッチャー"""
    
    def __init__(self):
        super().__init__(None)
    
    def matches(self, actual: Any) -> bool:
        return isinstance(actual, int) and actual % 2 == 0
    
    def describe_mismatch(self, actual: Any) -> str:
        if not isinstance(actual, int):
            return f"was {type(actual).__name__} {actual}, expected int"
        return f"was odd number {actual}"
    
    def describe_expected(self) -> str:
        return "even number"

def is_even() -> SmartMatcher:
    """偶数マッチャーを作成する便利関数"""
    return SmartMatcher(ToBeEvenMatcher())

# 使用例
def test_custom_matcher():
    assert 4 == is_even()  # 成功
    assert not (3 == is_even())  # 成功
```

## 実用例

### API レスポンスの検証

```python
def test_api_response():
    response = get_user_api(123)
    
    assert response == {
        "id": greater_than(100),
        "username": regex(r"^[a-zA-Z0-9_]+$"),
        "email": regex(r"^[\w\.-]+@[\w\.-]+\.\w+$"),
        "created_at": around_now(),
        "is_active": any_of(True, False)
    }
```

### ネストされたデータの検証

```python
def test_nested_data():
    data = {
        "user": {
            "profile": {
                "age": 25,
                "bio": "Software developer"
            }
        },
        "metadata": {
            "version": "1.2.3",
            "timestamp": datetime.now()
        }
    }
    
    assert data == {
        "user": {
            "profile": {
                "age": greater_than(18),
                "bio": contains("developer")
            }
        },
        "metadata": {
            "version": regex(r"\d+\.\d+\.\d+"),
            "timestamp": around_now()
        }
    }
```

## API リファレンス

| 関数 | 説明 | 例 |
|------|------|-----|
| `regex(pattern, flags=0)` | 正規表現マッチング | `assert "test123" == regex(r"test\\d+")` |
| `around_now(seconds=60)` | 現在時刻の前後N秒以内 | `assert datetime.now() == around_now()` |
| `greater_than(value)` | 指定値より大きい | `assert 10 == greater_than(5)` |
| `less_than(value)` | 指定値より小さい | `assert 3 == less_than(10)` |
| `any_of(*values)` | いずれかの値と一致 | `assert "success" == any_of("success", "ok")` |
| `contains(substring)` | 部分文字列を含む | `assert "hello world" == contains("world")` |

## 開発

### 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/your-username/mini-matchers.git
cd mini-matchers

# 依存関係のインストール
uv sync

# テストの実行
uv run pytest

# 型チェック
uv run mypy mini_matchers/
```

### コントリビューション

1. フォークしてブランチを作成
2. 変更を実装
3. テストを追加・実行
4. プルリクエストを作成

## ライセンス

MIT License

## 変更履歴

### v0.1.0 (開発中)

- スマートアサーション機能の実装
- 基本マッチャー群（regex, around_now, greater_than等）
- 型安全なProtocolベースの設計