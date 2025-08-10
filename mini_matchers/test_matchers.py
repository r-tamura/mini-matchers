"""
mini-matchers のテスト

すべてのマッチャー機能をテストします。
"""

import re
import pytest
from datetime import datetime, timedelta
from .matchers import (
    MatcherProtocol,
    BaseMatcherMixin,
    SmartMatcher,
    regex,
    around_now,
    greater_than,
    less_than,
    any_of,
    contains,
    RegexMatcher,
    AroundNowMatcher,
    GreaterThanMatcher,
    LessThanMatcher,
    AnyOfMatcher,
    ContainsMatcher,
)


# ===== テスト用のモッククラス =====

class MockMatcher(BaseMatcherMixin):
    """テスト用の具体的なマッチャー実装"""
    
    def __init__(self, expected: int):
        super().__init__(expected)
        self._should_match = True
        
    def matches(self, actual) -> bool:
        """テスト用のマッチング実装"""
        return self._should_match and actual == self.expected
        
    def describe_mismatch(self, actual) -> str:
        """テスト用のミスマッチ説明"""
        return f"was {actual}"
        
    def set_should_match(self, should_match: bool):
        """テスト用のマッチング結果制御"""
        self._should_match = should_match


class TypeSafeMatcher(BaseMatcherMixin):
    """型安全性テスト用のマッチャー実装"""
    
    def __init__(self, expected: int):
        super().__init__(expected)
        
    def matches(self, actual) -> bool:
        """型安全なマッチング実装"""
        return isinstance(actual, int) and actual == self.expected
        
    def describe_mismatch(self, actual) -> str:
        """型安全なミスマッチ説明"""
        if not isinstance(actual, int):
            return f"was {type(actual).__name__} {actual}, expected int"
        return f"was {actual}"


# ===== ベースマッチャーのテスト =====

class TestBaseMatcherMixin:
    """BaseMatcherMixinクラスのテスト"""
    
    def test_initialization(self):
        """初期化のテスト"""
        matcher = MockMatcher(42)
        assert matcher.expected == 42
        assert matcher.negated == False
        
    def test_describe_expected(self):
        """期待値説明のテスト"""
        matcher = MockMatcher(42)
        assert matcher.describe_expected() == "42"
        
        # 文字列の場合
        matcher = MockMatcher("test")
        assert matcher.describe_expected() == "test"
        
    def test_successful_assertion(self):
        """成功するアサーションのテスト"""
        matcher = MockMatcher(42)
        # 例外が発生しないことを確認
        matcher(42)
        
    def test_failed_assertion(self):
        """失敗するアサーションのテスト"""
        matcher = MockMatcher(42)
        matcher.set_should_match(False)
        
        with pytest.raises(AssertionError) as exc_info:
            matcher(99)
            
        error_message = str(exc_info.value)
        assert "Expected 42" in error_message
        assert "was 99" in error_message
        
    def test_negated_successful_assertion(self):
        """否定された成功するアサーションのテスト"""
        matcher = MockMatcher(42)
        matcher.negated = True
        matcher.set_should_match(False)  # マッチしない場合、否定で成功
        
        # 例外が発生しないことを確認
        matcher(99)
        
    def test_negated_failed_assertion(self):
        """否定された失敗するアサーションのテスト"""
        matcher = MockMatcher(42)
        matcher.negated = True
        matcher.set_should_match(True)  # マッチする場合、否定で失敗
        
        with pytest.raises(AssertionError) as exc_info:
            matcher(42)
            
        error_message = str(exc_info.value)
        assert "Expected not 42" in error_message
        assert "but was 42" in error_message
        
    def test_error_message_building(self):
        """エラーメッセージ構築のテスト"""
        matcher = MockMatcher(42)
        matcher.set_should_match(False)
        
        # 通常のエラーメッセージ
        error_msg = matcher._build_error_message(99)
        assert error_msg == "Expected 42, but was 99"
        
        # 否定されたエラーメッセージ
        matcher.negated = True
        error_msg = matcher._build_error_message(42)
        assert error_msg == "Expected not 42, but was 42"


class TestMatcherProtocol:
    """MatcherProtocolのテスト"""
    
    def test_protocol_compliance(self):
        """プロトコル準拠のテスト"""
        matcher = MockMatcher(42)
        
        # MatcherProtocolのメソッドが実装されていることを確認
        assert hasattr(matcher, 'negated')
        assert hasattr(matcher, 'matches')
        assert hasattr(matcher, 'describe_mismatch')
        assert hasattr(matcher, 'describe_expected')
        assert callable(matcher)
        
        # 型チェック（実行時）
        assert isinstance(matcher.negated, bool)
        assert callable(matcher.matches)
        assert callable(matcher.describe_mismatch)
        assert callable(matcher.describe_expected)
        
    def test_protocol_methods_return_types(self):
        """プロトコルメソッドの戻り値型のテスト"""
        matcher = MockMatcher(42)
        
        # matches メソッドは bool を返す
        result = matcher.matches(42)
        assert isinstance(result, bool)
        
        # describe_mismatch メソッドは str を返す
        description = matcher.describe_mismatch(99)
        assert isinstance(description, str)
        
        # describe_expected メソッドは str を返す
        expected_desc = matcher.describe_expected()
        assert isinstance(expected_desc, str)


class TestTypeSafety:
    """型安全性のテスト"""
    
    def test_matcher_protocol_compliance(self):
        """MatcherProtocolへの準拠テスト"""
        matcher = TypeSafeMatcher(42)
        
        # MatcherProtocolの属性とメソッドが存在することを確認
        assert hasattr(matcher, 'negated')
        assert hasattr(matcher, 'matches')
        assert hasattr(matcher, 'describe_mismatch')
        assert hasattr(matcher, 'describe_expected')
        assert callable(matcher)
        
        # 型の確認
        assert isinstance(matcher.negated, bool)
        
    def test_protocol_method_signatures(self):
        """プロトコルメソッドのシグネチャテスト"""
        matcher = TypeSafeMatcher(42)
        
        # matches メソッドの戻り値型
        result = matcher.matches(42)
        assert isinstance(result, bool)
        
        # describe_mismatch メソッドの戻り値型
        mismatch_desc = matcher.describe_mismatch("not_int")
        assert isinstance(mismatch_desc, str)
        
        # describe_expected メソッドの戻り値型
        expected_desc = matcher.describe_expected()
        assert isinstance(expected_desc, str)
        
    def test_subclass_implementation_requirement(self):
        """サブクラスでの実装要求テスト"""
        class IncompleteMatcherMixin(BaseMatcherMixin):
            """不完全な実装のマッチャー"""
            pass
            
        incomplete_matcher = IncompleteMatcherMixin(42)
        
        # matches メソッドが実装されていない場合の例外
        with pytest.raises(NotImplementedError):
            incomplete_matcher.matches(42)
            
        # describe_mismatch メソッドが実装されていない場合の例外
        with pytest.raises(NotImplementedError):
            incomplete_matcher.describe_mismatch(42)


# ===== スマートマッチャーのテスト =====

class TestSmartMatcher:
    """SmartMatcherクラスのテスト"""
    
    def test_smart_matcher_equality_success(self):
        """SmartMatcherの等価性チェック成功ケース"""
        matcher = SmartMatcher(RegexMatcher(r"\d+"))
        
        # == 演算子でマッチング
        assert "123" == matcher
        assert matcher == "456"
    
    def test_smart_matcher_equality_failure(self):
        """SmartMatcherの等価性チェック失敗ケース"""
        matcher = SmartMatcher(RegexMatcher(r"\d+"))
        
        # マッチしない場合はFalse
        assert not ("abc" == matcher)
        assert not (matcher == "xyz")
    
    def test_smart_matcher_repr(self):
        """SmartMatcherの文字列表現"""
        matcher = SmartMatcher(RegexMatcher(r"\d+"))
        repr_str = repr(matcher)
        
        assert "SmartMatcher" in repr_str
        assert "string matching" in repr_str


# ===== 便利関数のテスト =====

class TestRegexFunction:
    """regex関数のテスト"""
    
    def test_regex_basic_matching(self):
        """基本的な正規表現マッチング"""
        pattern_matcher = regex(r"\d{3}")
        
        assert "123" == pattern_matcher
        assert "abc123def" == pattern_matcher
        assert not ("abc" == pattern_matcher)
    
    def test_regex_with_flags(self):
        """フラグ付き正規表現マッチング"""
        case_insensitive = regex(r"hello", re.IGNORECASE)
        
        assert "HELLO" == case_insensitive
        assert "Hello" == case_insensitive
        assert "hello" == case_insensitive
    
    def test_regex_email_pattern(self):
        """メールアドレスパターンのテスト"""
        email_pattern = regex(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        
        assert "test@example.com" == email_pattern
        assert "user.name@domain.co.jp" == email_pattern
        assert not ("invalid-email" == email_pattern)
    
    def test_regex_with_non_string(self):
        """文字列以外の値でのテスト"""
        pattern_matcher = regex(r"\d+")
        
        assert not (123 == pattern_matcher)
        assert not (None == pattern_matcher)
        assert not ([] == pattern_matcher)


class TestAroundNowFunction:
    """around_now関数のテスト"""
    
    def test_around_now_with_datetime(self):
        """datetime オブジェクトでのテスト"""
        now_matcher = around_now(60)  # 1分以内
        
        # 現在時刻
        assert datetime.now() == now_matcher
        
        # 30秒前
        past_time = datetime.now() - timedelta(seconds=30)
        assert past_time == now_matcher
        
        # 30秒後
        future_time = datetime.now() + timedelta(seconds=30)
        assert future_time == now_matcher
    
    def test_around_now_with_iso_string(self):
        """ISO形式文字列でのテスト"""
        now_matcher = around_now(60)
        
        # 現在時刻のISO文字列
        now_iso = datetime.now().isoformat()
        assert now_iso == now_matcher
    
    def test_around_now_tolerance(self):
        """許容範囲のテスト"""
        strict_matcher = around_now(10)  # 10秒以内
        
        # 5秒前は成功
        recent_time = datetime.now() - timedelta(seconds=5)
        assert recent_time == strict_matcher
        
        # 15秒前は失敗
        old_time = datetime.now() - timedelta(seconds=15)
        assert not (old_time == strict_matcher)
    
    def test_around_now_with_invalid_type(self):
        """無効な型でのテスト"""
        now_matcher = around_now()
        
        assert not (123 == now_matcher)
        assert not ("invalid-date" == now_matcher)
        assert not (None == now_matcher)


class TestNumericComparisons:
    """数値比較関数のテスト"""
    
    def test_greater_than(self):
        """greater_than関数のテスト"""
        gt_matcher = greater_than(5)
        
        assert 10 == gt_matcher
        assert 5.1 == gt_matcher
        assert not (5 == gt_matcher)
        assert not (3 == gt_matcher)
        assert not ("10" == gt_matcher)  # 文字列は失敗
    
    def test_less_than(self):
        """less_than関数のテスト"""
        lt_matcher = less_than(10)
        
        assert 5 == lt_matcher
        assert 9.9 == lt_matcher
        assert not (10 == lt_matcher)
        assert not (15 == lt_matcher)
        assert not ("5" == lt_matcher)  # 文字列は失敗
    
    def test_numeric_with_float(self):
        """浮動小数点数でのテスト"""
        gt_matcher = greater_than(3.14)
        lt_matcher = less_than(3.14)
        
        assert 3.15 == gt_matcher
        assert 3.13 == lt_matcher
        assert not (3.14 == gt_matcher)
        assert not (3.14 == lt_matcher)


class TestAnyOfFunction:
    """any_of関数のテスト"""
    
    def test_any_of_basic(self):
        """基本的なany_ofテスト"""
        status_matcher = any_of("success", "completed", "done")
        
        assert "success" == status_matcher
        assert "completed" == status_matcher
        assert "done" == status_matcher
        assert not ("failed" == status_matcher)
    
    def test_any_of_mixed_types(self):
        """混合型でのany_ofテスト"""
        mixed_matcher = any_of(1, "one", 1.0, True)
        
        assert 1 == mixed_matcher
        assert "one" == mixed_matcher
        assert 1.0 == mixed_matcher
        assert True == mixed_matcher
        assert not (2 == mixed_matcher)
    
    def test_any_of_empty(self):
        """空のany_ofテスト"""
        empty_matcher = any_of()
        
        assert not ("anything" == empty_matcher)
        assert not (123 == empty_matcher)


class TestContainsFunction:
    """contains関数のテスト"""
    
    def test_contains_basic(self):
        """基本的なcontainsテスト"""
        hello_matcher = contains("hello")
        
        assert "hello world" == hello_matcher
        assert "say hello" == hello_matcher
        assert "hello" == hello_matcher
        assert not ("hi there" == hello_matcher)
    
    def test_contains_case_sensitive(self):
        """大文字小文字を区別するテスト"""
        hello_matcher = contains("Hello")
        
        assert "Hello World" == hello_matcher
        assert not ("hello world" == hello_matcher)
    
    def test_contains_with_non_string(self):
        """文字列以外でのテスト"""
        hello_matcher = contains("hello")
        
        assert not (123 == hello_matcher)
        assert not (["hello"] == hello_matcher)
        assert not (None == hello_matcher)


# ===== 複雑なシナリオのテスト =====

class TestComplexScenarios:
    """複雑なシナリオのテスト"""
    
    def test_dictionary_with_smart_matchers(self):
        """辞書でのスマートマッチャー使用"""
        actual = {
            "id": 123,
            "name": "Test User",
            "email": "test@example.com",
            "created_at": datetime.now(),
            "status": "active"
        }
        
        expected = {
            "id": greater_than(100),
            "name": contains("User"),
            "email": regex(r"^[\w\.-]+@[\w\.-]+\.\w+$"),
            "created_at": around_now(),
            "status": any_of("active", "inactive", "pending")
        }
        
        assert actual == expected
    
    def test_nested_dictionary(self):
        """ネストされた辞書でのテスト"""
        actual = {
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
        
        expected = {
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
        
        assert actual == expected
    
    def test_list_with_smart_matchers(self):
        """リストでのスマートマッチャー使用"""
        actual = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]
        
        expected = [
            {"id": 1, "name": contains("Item")},
            {"id": 2, "name": contains("Item")},
            {"id": 3, "name": contains("Item")}
        ]
        
        assert actual == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])