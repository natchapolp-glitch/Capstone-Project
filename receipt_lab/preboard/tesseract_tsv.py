"""Tesseract TSV has literal quote characters, not CSV-quoted multiline fields."""
import csv
import io


def parse_tsv(text):
    groups = {}
    for row in csv.DictReader(io.StringIO(text), delimiter='\t', quoting=csv.QUOTE_NONE):
        if None in row or any(row.get(k) is None for k in ['level','page_num','block_num','par_num','line_num','text']):
            raise ValueError('Malformed Tesseract TSV row')
        if row['level'] != '5' or not row['text'].strip():
            continue
        key = tuple(row[k] for k in ['page_num','block_num','par_num','line_num'])
        groups.setdefault(key, []).append(row)
    return [{'text':' '.join(w['text'] for w in words), 'words':words} for words in groups.values()]
