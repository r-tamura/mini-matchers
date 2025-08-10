"""
mini-matchers: 軽量スマートアサーションライブラリ

通常のassert文でマッチャーオブジェクトを使用できる機能を提供します。
辞書の値にマッチャーを埋め込んで、柔軟な比較を行うことができます。
"""

import re
from datetime import datetime, timedelta
from typing import Any, Union, Tuple, Protocol


# ===== プロトコルとベースクラス =====

class MatcherProtocol(Protocol):
    """すべてのマッチャーが実装すべきプロトコル"""
    
    negated: bool
    
    def matches(self, actual: Any) -> bool:
        """実際の値がマッチするかを判定"""
        ...
        
    def describe_mismatch(self, actual: Any) -> str:
        """マッチしない場合の説明を生成"""
        ...
        
    def describe_expected(self) -> str:
        """期待値の説明を生成"""
        ...
        
    def __call__(self, actual: Any) -> None:
        """アサーション実行"""
        ...


class BaseMatcherMixin:
    """共通機能を提供するミックスインクラス"""
    
    def __init__(self, expected: Any):
        """ベースマッチャーの初期化"""
        self.expected = expected
        self.negated = False
        
    def matches(self, actual: Any) -> bool:
        """実際の値がマッチするかを判定（サブクラスで実装）"""
        raise NotImplementedError("Subclasses must implement matches method")
        
    def describe_mismatch(self, actual: Any) -> str:
        """マッチしない場合の説明を生成（サブクラスで実装）"""
        raise NotImplementedError("Subclasses must implement describe_mismatch method")
        
    def describe_expected(self) -> str:
        """期待値の説明を生成"""
        return str(self.expected)
        
    def __call__(self, actual: Any) -> None:
        """アサーション実行"""
        result = self.matches(actual)
        if self.negated:
            result = not result
            
        if not result:
            raise AssertionError(self._build_error_message(actual))
            
    def _build_error_message(self, actual: Any) -> str:
        """エラーメッセージを構築"""
        if self.negated:
            return f"Expected not {self.describe_expected()}, but was {actual}"
        else:
            return f"Expected {self.describe_expected()}, but {self.describe_mismatch(actual)}"


# ===== スマートマッチャーシステム =====

class SmartMatcher:
    """スマートアサーション用のベースクラス
    
    == 演算子をオーバーライドして、通常のassert文でマッチャーを使用可能にします。
    """
    
    def __init__(self, matcher: BaseMatcherMixin):
        """SmartMatcherを初期化"""
        self.matcher = matcher
    
    def __eq__(self, other: Any) -> bool:
        """== 演算子をオーバーライドしてマッチング処理を実行"""
        try:
            # マッチャーを実行（例外が発生しなければマッチ成功）
            self.matcher(other)
            return True
        except AssertionError:
            return False
    
    def __repr__(self) -> str:
        """SmartMatcherの文字列表現"""
        return f"SmartMatcher({self.matcher.describe_expected()})"


# ===== 具体的なマッチャークラス =====

class RegexMatcher(BaseMatcherMixin):
    """正規表現にマッチするかチェックするマッチャー"""
    
    def __init__(self, pattern: str, flags: int = 0):
        super().__init__(pattern)
        self.flags = flags
        self.compiled_pattern = re.compile(pattern, flags)
    
    def matches(self, actual: Any) -> bool:
        if not isinstance(actual, str):
            return False
        return bool(self.compiled_pattern.search(actual))
    
    def describe_mismatch(self, actual: Any) -> str:
        if not isinstance(actual, str):
            return f"was {type(actual).__name__} {actual}, expected string"
        return f"was '{actual}'"
    
    def describe_expected(self) -> str:
        return f"string matching /{self.expected}/"


class AroundNowMatcher(BaseMatcherMixin):
    """現在時刻の前後指定秒数以内かチェックするマッチャー"""
    
    def __init__(self, tolerance_seconds: int):
        super().__init__(tolerance_seconds)
        self.tolerance = timedelta(seconds=tolerance_seconds)
        self.now = datetime.now()
    
    def matches(self, actual: Any) -> bool:
        if isinstance(actual, str):
            try:
                # ISO形式の文字列をパース
                actual_dt = datetime.fromisoformat(actual.replace('Z', '+00:00'))
            except ValueError:
                return False
        elif isinstance(actual, datetime):
            actual_dt = actual
        else:
            return False
        
        diff = abs(actual_dt.replace(tzinfo=None) - self.now)
        return diff <= self.tolerance
    
    def describe_mismatch(self, actual: Any) -> str:
        if isinstance(actual, str):
            return f"was string '{actual}'"
        elif isinstance(actual, datetime):
            diff = abs(actual - self.now)
            return f"was {actual}, which is {diff.total_seconds():.1f} seconds from now"
        else:
            return f"was {type(actual).__name__} {actual}, expected datetime or ISO string"
    
    def describe_expected(self) -> str:
        return f"datetime within {self.expected} seconds of {self.now}"


class GreaterThanMatcher(BaseMatcherMixin):
    """指定値より大きいかチェックするマッチャー"""
    
    def matches(self, actual: Any) -> bool:
        if not isinstance(actual, (int, float)) or not isinstance(self.expected, (int, float)):
            return False
        return actual > self.expected
    
    def describe_mismatch(self, actual: Any) -> str:
        if not isinstance(actual, (int, float)):
            return f"was {type(actual).__name__} {actual}, expected number"
        return f"was {actual}"
    
    def describe_expected(self) -> str:
        return f"number greater than {self.expected}"


class LessThanMatcher(BaseMatcherMixin):
    """指定値より小さいかチェックするマッチャー"""
    
    def matches(self, actual: Any) -> bool:
        if not isinstance(actual, (int, float)) or not isinstance(self.expected, (int, float)):
            return False
        return actual < self.expected
    
    def describe_mismatch(self, actual: Any) -> str:
        if not isinstance(actual, (int, float)):
            return f"was {type(actual).__name__} {actual}, expected number"
        return f"was {actual}"
    
    def describe_expected(self) -> str:
        return f"number less than {self.expected}"


class AnyOfMatcher(BaseMatcherMixin):
    """指定された値のいずれかと一致するかチェックするマッチャー"""
    
    def __init__(self, values: Tuple[Any, ...]):
        super().__init__(values)
        self.values = values
    
    def matches(self, actual: Any) -> bool:
        return actual in self.values
    
    def describe_mismatch(self, actual: Any) -> str:
        return f"was {actual}"
    
    def describe_expected(self) -> str:
        return f"any of {list(self.values)}"


class ContainsMatcher(BaseMatcherMixin):
    """指定された部分文字列を含むかチェックするマッチャー"""
    
    def matches(self, actual: Any) -> bool:
        if not isinstance(actual, str):
            return False
        return self.expected in actual
    
    def describe_mismatch(self, actual: Any) -> str:
        if not isinstance(actual, str):
            return f"was {type(actual).__name__} {actual}, expected string"
        return f"was '{actual}'"
    
    def describe_expected(self) -> str:
        return f"string containing '{self.expected}'"


# ===== 便利な関数群 =====

def regex(pattern: str, flags: int = 0) -> SmartMatcher:
    """正規表現マッチャーを作成
    
    Args:
        pattern: 正規表現パターン
        flags: 正規表現フラグ（re.IGNORECASE等）
        
    Returns:
        SmartMatcher: 正規表現マッチャー
        
    Example:
        assert "test123" == regex(r"test\\d+")
    """
    return SmartMatcher(RegexMatcher(pattern, flags))


def around_now(tolerance_seconds: int = 60) -> SmartMatcher:
    """現在時刻の前後指定秒数以内かチェックするマッチャーを作成
    
    Args:
        tolerance_seconds: 許容する秒数（デフォルト: 60秒）
        
    Returns:
        SmartMatcher: 時刻範囲マッチャー
        
    Example:
        assert datetime.now() == around_now()
        assert datetime.now() == around_now(300)  # 5分以内
    """
    return SmartMatcher(AroundNowMatcher(tolerance_seconds))


def greater_than(value: Union[int, float]) -> SmartMatcher:
    """指定値より大きいかチェックするマッチャーを作成
    
    Args:
        value: 比較する値
        
    Returns:
        SmartMatcher: 大小比較マッチャー
        
    Example:
        assert 10 == greater_than(5)
    """
    return SmartMatcher(GreaterThanMatcher(value))


def less_than(value: Union[int, float]) -> SmartMatcher:
    """指定値より小さいかチェックするマッチャーを作成
    
    Args:
        value: 比較する値
        
    Returns:
        SmartMatcher: 大小比較マッチャー
        
    Example:
        assert 3 == less_than(10)
    """
    return SmartMatcher(LessThanMatcher(value))


def any_of(*values) -> SmartMatcher:
    """指定された値のいずれかと一致するかチェックするマッチャーを作成
    
    Args:
        *values: 候補となる値のリスト
        
    Returns:
        SmartMatcher: 選択肢マッチャー
        
    Example:
        assert "success" == any_of("success", "completed", "done")
    """
    return SmartMatcher(AnyOfMatcher(values))


def contains(substring: str) -> SmartMatcher:
    """指定された部分文字列を含むかチェックするマッチャーを作成
    
    Args:
        substring: 検索する部分文字列
        
    Returns:
        SmartMatcher: 文字列包含マッチャー
        
    Example:
        assert "Hello World" == contains("World")
    """
    return SmartMatcher(ContainsMatcher(substring))