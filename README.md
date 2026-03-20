# Screen Time Exporter

macOSのスクリーンタイムデータを自動的にスクリーンショットし、OCRで解析してCSVに出力するコマンドラインツール。

## 必要条件

- macOS Ventura (13.0) 以降
- Python 3.10+
- アクセシビリティ権限（システム環境設定 > プライバシーとセキュリティ > アクセシビリティ でターミナルを許可）

## インストール

```bash
pip install -e .
```

## 使い方

```bash
# 基本的な使い方（開始日と終了日を指定）
screentime-export --start-date 2026-03-01 --end-date 2026-03-20 --output screentime.csv

# ヘルプを表示
screentime-export --help
```

## オプション

| オプション | 説明 |
|-----------|------|
| `--start-date` | 開始日 (YYYY-MM-DD形式) |
| `--end-date` | 終了日 (YYYY-MM-DD形式) |
| `--output`, `-o` | 出力ファイル名 (デフォルト: screentime.csv) |

## 出力フォーマット

```csv
date,category,app_name,duration_minutes
2026-03-01,ソーシャルネットワーキング,Twitter,45
2026-03-01,ソーシャルネットワーキング,LINE,30
2026-03-01,仕事効率化,Slack,120
```

## 注意事項

- 実行前にアクセシビリティ権限を付与してください
- 実行中はマウス/キーボードの操作を避けてください
- スクリーンタイムが有効になっている必要があります

## ライセンス

MIT
