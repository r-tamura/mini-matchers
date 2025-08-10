"""
mini-matchers のテスト

すべてのマッチャー機能をテストします。
"""

import re
import pytest
from datetime import datetime, timedelta
from .matchers import (
    MatcherProtocol,
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


# ===== 不要なテストクラスを削除しました =====
# 型安全性はmypyで保証、基本機能は実際のマッチャーテストでカバー


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