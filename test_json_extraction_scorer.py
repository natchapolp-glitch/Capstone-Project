import copy
import json
import tempfile
import unittest
from pathlib import Path
from json_extraction_scorer import score, process_pair, strict_json_loads


def receipt():
    return {"transaction_date": "2026-10-18", "merchant": "Example store",
            "grand_total": 100, "currency": "THB",
            "items": [{"name": "rice", "quantity": 1, "unit": "bag",
                       "unit_price": 100, "line_total": 100}]}


class ReceiptScorerTests(unittest.TestCase):
    def test_every_promised_field_changes_score(self):
        for location, key, wrong in [(None, "transaction_date", "1999-01-01"),
                (None, "merchant", "Wrong store"), (None, "grand_total", 9999),
                (None, "currency", "USD"), (0, "unit", "wrong"),
                (0, "line_total", 9999), (0, "name", "wrong"),
                (0, "quantity", 9), (0, "unit_price", 999)]:
            with self.subTest(field=key):
                gt = receipt(); hyp = copy.deepcopy(gt)
                target = hyp if location is None else hyp["items"][location]
                target[key] = wrong
                result = score(gt, hyp)
                self.assertEqual(result["exact_match"], 0)
                self.assertLess(result["f1"], 1)

    def test_original_regression(self):
        gt = receipt(); hyp = receipt()
        hyp.update(transaction_date="1999-01-01", merchant="Wrong", grand_total=9999, currency="USD")
        hyp["items"][0].update(unit="wrong", line_total=9999)
        self.assertEqual(score(gt, hyp)["f1"], 0.3333)

    def test_numeric_equivalence(self):
        gt = receipt(); hyp = receipt(); hyp["grand_total"] = 100.0
        self.assertEqual(score(gt, hyp)["exact_match"], 1)

    def test_legacy_and_nonobject_are_rejected(self):
        for hyp in [{"date": "2026-10-18", "store_name": "Example", "total": 100}, [], None]:
            self.assertEqual(score(receipt(), hyp)["schema_valid"], 0)

    def test_invalid_truth_raises(self):
        with self.assertRaises(ValueError):
            score({}, receipt())

    def test_schema_rejects_wrong_types_unknown_fields_and_missing_fields(self):
        for change in [lambda x: x.update(currency=3), lambda x: x.update(extra=1),
                       lambda x: x.pop("merchant"), lambda x: x.update(grand_total=True),
                       lambda x: x.update(grand_total=float("nan"))]:
            hyp = receipt(); change(hyp)
            self.assertEqual(score(receipt(), hyp)["schema_valid"], 0)

    def test_added_item_reduces_precision(self):
        hyp = receipt(); hyp["items"].append(dict(hyp["items"][0], name="milk"))
        result = score(receipt(), hyp)
        self.assertEqual(result["hallucination_count"], 1)
        self.assertLess(result["precision"], 1)

    def test_reordered_duplicate_names(self):
        gt = receipt(); gt["items"].append(dict(gt["items"][0], quantity=2, line_total=200))
        hyp = copy.deepcopy(gt); hyp["items"].reverse()
        self.assertEqual(score(gt, hyp)["exact_match"], 1)

    def test_null_does_not_hide_invented_value(self):
        gt = receipt(); gt["merchant"] = None
        self.assertEqual(score(gt, receipt())["exact_match"], 0)

    def test_missing_output_is_a_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "gt.json"; path.write_text(json.dumps(receipt()), encoding="utf-8")
            result = process_pair(path, Path(temp) / "missing.json")
            self.assertEqual(result["json_valid"], 0)
            self.assertEqual(result["exact_match"], 0)

    def test_large_finite_integer_is_scored_without_overflow(self):
        prediction=receipt();prediction['grand_total']=10**400
        result=score(receipt(),prediction)
        self.assertEqual(result['schema_valid'],1)
        self.assertLess(result['f1'],1)

    def test_duplicate_keys_and_non_json_constants_are_not_silently_parsed(self):
        for text in ['{"items":[{"name":"a","name":"b"}]}','{"grand_total":NaN}','{"grand_total":Infinity}']:
            with self.assertRaises(ValueError):strict_json_loads(text)

    def test_empty_strings_in_unmatched_items_use_the_same_presence_rule(self):
        prediction=receipt()
        prediction['items'].append({'name':'milk','quantity':None,'unit':'','unit_price':None,'line_total':None})
        self.assertEqual(score(receipt(),prediction)['precision'],0.9)


if __name__ == "__main__":
    unittest.main()
