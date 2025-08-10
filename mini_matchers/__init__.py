"""
mini-matchers: 軽量スマートアサーションライブラリ

通常のassert文でマッチャーオブジェクトを使用できる機能を提供し、
動的な値を含む複雑なテストシナリオを簡潔に記述できます。
"""

from .matchers import (
    MatcherProtocol,
    SmartMatcher,
    regex,
    around_now,
    greater_than,
    less_than,
    any_of,
    contains,
)

# パブリックAPIのエクスポート
__all__ = [
    # コアクラス（拡張用）
    'MatcherProtocol',
    
    # スマートマッチャー（メイン機能）
    'SmartMatcher',
    'regex',
    'around_now',
    'greater_than',
    'less_than',
    'any_of',
    'contains',
]

__version__ = "0.1.0"