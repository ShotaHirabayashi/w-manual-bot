# Title


python manage.py load_qa_data docs/rag-text.txt --doc-title "フロントマニュアル" --type qa --clear-db


python manage.py import_guidelines
python manage.py import_guidelines --file docs/guideline_unified.txt
python manage.py import_guidelines --clear  # 既存削除してから追加
