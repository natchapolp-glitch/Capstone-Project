import unittest
from receipt_lab.preboard.tesseract_tsv import parse_tsv


class TesseractTSVTests(unittest.TestCase):
    def test_quotes_are_literal_not_multiline_csv_fields(self):
        header='level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n'
        data=header+'5\t1\t1\t1\t1\t1\t1\t2\t3\t4\t95\t"\n'
        data+='5\t1\t1\t1\t1\t2\t5\t2\t3\t4\t94\tmilk\n'
        data+='5\t1\t1\t1\t2\t1\t1\t8\t3\t4\t93\t"sale"\n'
        rows=parse_tsv(data)
        self.assertEqual([r['text'] for r in rows], ['" milk','"sale"'])
        self.assertEqual(len(rows[0]['words']),2)
        self.assertFalse(any('\t' in r['text'] or '\n' in r['text'] for r in rows))

    def test_malformed_table_is_failure_not_receipt_text(self):
        with self.assertRaises(ValueError):
            parse_tsv('level\ttext\n5\tbad\textra\n')
