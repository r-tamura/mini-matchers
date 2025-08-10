# Examples

このディレクトリには、pytest-custom-matchersライブラリの使用例が含まれています。

## ファイル構成

### `smart_assertions.py`
mini-matchersライブラリを使用した実用的なサンプルコードです。通常の`assert`文でマッチャーオブジェクトを使用する方法を学べます。

**含まれる内容:**
- ライブラリの基本的な使用方法
- 正規表現、時刻範囲、数値比較マッチャーの実用例
- ネストされたデータ構造での使用例
- API レスポンス検証の実例

**実行方法:**
```bash
# テストとして実行
uv run pytest examples/smart_assertions.py -v

# スクリプトとして実行
uv run python examples/smart_assertions.py
```

### `custom_matchers.py`
独自のマッチャーを作成する方法を詳しく説明するサンプルコードです。BaseMatcherMixinを継承した様々な種類のマッチャーの実装例を提供しています。

**含まれる内容:**
- 偶数/奇数チェックマッチャー (`ToBeEvenMatcher`, `ToBeOddMatcher`)
- 正規表現マッチャー (`ToMatchRegexMatcher`)
- 長さチェックマッチャー (`ToHaveLengthMatcher`)
- 範囲チェックマッチャー (`ToBeInRangeMatcher`)
- 辞書キーチェックマッチャー (`ToHaveKeyMatcher`)
- カスタム条件マッチャー (`ToSatisfyMatcher`)
- 複合的なオブジェクト検証の例

**実行方法:**
```bash
# テストとして実行
uv run pytest examples/custom_matchers.py -v

# スクリプトとして実行
uv run python examples/custom_matchers.py
```

## 学習の進め方

1. **ライブラリの使用方法を学ぶ**: まず `smart_assertions.py` を読んで、mini-matchersライブラリの基本的な使用方法を理解してください。

2. **カスタマイズを学ぶ**: `custom_matchers.py` で独自のマッチャーの実装パターンを学んでください。

## 実際のプロジェクトでの使用

これらの例を参考に、あなたのプロジェクトに適したカスタムマッチャーを作成してください。

### マッチャー作成のベストプラクティス

1. **単一責任**: 各マッチャーは一つの明確な責任を持つ
2. **型安全性**: 適切な型チェックを実装する
3. **明確なエラーメッセージ**: テスト失敗時に分かりやすいメッセージを提供する
4. **テスト**: マッチャー自体もテストする
5. **ドキュメント**: 使用方法と期待される動作を明確に記述する

### よくあるパターン

- **値の比較**: `ToEqualMatcher`, `ToBeGreaterThanMatcher`
- **型チェック**: `isinstance()` を使用した型検証
- **コレクション操作**: `in` 演算子や `len()` 関数の活用
- **正規表現**: `re` モジュールを使用したパターンマッチング
- **カスタム条件**: ラムダ関数や関数を使用した柔軟な条件設定

## トラブルシューティング

### よくあるエラー

1. **ImportError**: パッケージのパスが正しく設定されているか確認してください
2. **TypeError**: マッチャーで適切な型チェックを実装してください
3. **AssertionError**: エラーメッセージが分かりやすいか確認してください

### デバッグのヒント

- `describe_mismatch()` メソッドで詳細な情報を提供する
- テスト実行時に `-v` オプションを使用して詳細な出力を確認する
- 型チェックには `mypy` を活用する
