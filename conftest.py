import sys
import os

# プロジェクトのルートディレクトリをPYTHONPATHに追加
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "functions"))
)
