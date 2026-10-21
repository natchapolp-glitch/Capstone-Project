"""Read-only evidence checks plus private HA login for the Robot browser suite."""
import hashlib
import json
import sqlite3
import time
import urllib.request
from pathlib import Path

from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class DemoEvidence:
    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self):
        self.work = Path.home() / 'SeminarLab/preboard'
        self.rid = None
        self.raw_before = None
        self.annotation_before = None

    def api(self, path):
        with urllib.request.urlopen('http://127.0.0.1:8090' + path, timeout=45) as response:
            return json.load(response)

    @keyword
    def Check_Preconditions(self):
        with sqlite3.connect(self.work / 'services/demo.sqlite') as db:
            assert db.execute('SELECT COUNT(*) FROM outbox WHERE sent_at IS NULL').fetchone()[0] == 0, 'Existing pending events must be reviewed separately'
        self.annotation_before = self.annotation_hashes()

    def annotation_hashes(self):
        return {str(p.relative_to(self.work)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (self.work / 'annotations').rglob('*') if p.is_file()}

    @keyword
    def Remember_Current_Run(self):
        driver = BuiltIn().get_library_instance('SeleniumLibrary').driver
        self.rid = driver.find_element(By.ID, 'saved').get_attribute('value')
        assert self.rid
        record = self.api('/api/receipt?id=' + self.rid)
        raw = record['raw_result']
        assert raw['status'] == 'pending_review', raw.get('error')
        assert raw['ocr']['status'] == 'ok' and raw['llm']['status'] == 'ok'
        assert raw['llm']['schema_valid'] is True
        self.raw_before = raw
        return self.rid

    @keyword
    def Use_Existing_Test_Run(self, receipt_id):
        record = self.api('/api/receipt?id=' + receipt_id)
        assert record['confirmed']['merchant'] == 'ROBOT FRAMEWORK TRANSPORT TEST - NOT HUMAN TRUTH'
        self.rid = receipt_id
        self.raw_before = record['raw_result']

    @keyword
    def Verify_Stored_Edit_And_HA(self):
        record = self.api('/api/receipt?id=' + self.rid)
        assert record['status'] == 'published'
        assert record['raw_result'] == self.raw_before, 'UI edits must preserve original model output'
        confirmed = record['confirmed']
        assert confirmed['merchant'] == 'ROBOT FRAMEWORK TRANSPORT TEST - NOT HUMAN TRUTH'
        assert confirmed['grand_total'] == 45 and len(confirmed['items']) == 1
        assert confirmed['items'][0]['name'] == 'AUTOMATED UI TEST ITEM'
        event_id = self.rid + ':' + str(record['revision'])
        states = self.api('/api/ha-status')
        assert states['reachable'] and len(states['entities']) == 2
        for entity in states['entities']:
            assert entity['event_id'] == event_id
            expected = 45 if entity['entity_id'].endswith('purchase_total') else 1
            assert float(entity['state']) == expected
        with sqlite3.connect(self.work / 'services/demo.sqlite') as db:
            assert db.execute('SELECT COUNT(*) FROM outbox WHERE receipt_id=?', (self.rid,)).fetchone()[0] == 1
            actor = db.execute('SELECT actor FROM edits WHERE receipt_id=?', (self.rid,)).fetchone()[0]
            assert actor == 'robot_framework_automated_test_not_human_ground_truth'
        assert self.annotation_hashes() == self.annotation_before, 'Human annotation files must stay unchanged'
        output = Path(BuiltIn().get_variable_value('${OUTPUT DIR}'))
        (output / 'transport_evidence.json').write_text(json.dumps({
            'receipt_id': self.rid, 'pipeline_run_id': self.raw_before['run_id'],
            'event_id': event_id, 'confirmed': confirmed, 'ha_readback': states,
            'purpose': 'Synthetic UI edits test persistence and transport; not semantic model accuracy or human review',
            'human_annotations_unchanged': True, 'raw_model_output_preserved': True,
        }, ensure_ascii=False, indent=2), encoding='utf-8')
        return event_id

    @keyword
    def Verify_Thai_Labels_And_Page(self):
        driver = BuiltIn().get_library_instance('SeleniumLibrary').driver
        text = driver.find_element(By.TAG_NAME, 'body').text
        assert '???' not in text and '\ufffd' not in text
        assert 'ผลจากเครื่องมือก่อนผู้ใช้แก้ไข' in text
        assert 'ตรวจสถานะปลายทาง' in text
        errors = [e for e in driver.get_log('browser') if e['level'] == 'SEVERE' and 'favicon.ico' not in e['message']]
        assert not errors, errors

    def deep_elements(self, selector):
        driver = BuiltIn().get_library_instance('SeleniumLibrary').driver
        return driver.execute_script('''
        const result=[];
        function visit(root){result.push(...root.querySelectorAll(argumentsSelector));for(const e of root.querySelectorAll('*'))if(e.shadowRoot)visit(e.shadowRoot);}
        const argumentsSelector=arguments[0];visit(document);return result;
        ''', selector)

    @keyword
    def Sign_In_To_Home_Assistant_Privately(self):
        # Robot receives no credentials as arguments or return values.
        auth = json.loads((self.work / 'services/ha_auth.json').read_text(encoding='utf-8'))
        wait = WebDriverWait(BuiltIn().get_library_instance('SeleniumLibrary').driver, 30)
        def visible(selector):
            return [e for e in self.deep_elements(selector) if e.is_displayed()]
        username = wait.until(lambda _: visible('input[name="username"]'))[0]
        password = visible('input[name="password"]')[0]
        username.send_keys(auth['username'])
        password.send_keys(auth['password'])
        password.submit()

    @keyword
    def Home_Assistant_State_Page_Should_Load(self):
        elements = self.deep_elements('ha-panel-config')
        assert elements, 'Home Assistant main config panel has not loaded'
        headings = self.deep_elements('h1, h2, ha-tab, wa-tab, md-primary-tab, ha-button, button')
        labels = ' '.join(e.text for e in headings)
        assert 'current entity states' in labels.lower() or 'สถานะ' in labels, labels[:500]

    @keyword
    def Home_Assistant_Should_Display_Test_Event(self):
        driver = BuiltIn().get_library_instance('SeleniumLibrary').driver
        text = driver.execute_script('''
        function texts(root){let s=root.innerText||Array.from(root.children||[]).map(e=>e.innerText||'').join(' ');for(const e of root.querySelectorAll('*'))if(e.shadowRoot)s+=' '+texts(e.shadowRoot);return s;}
        return texts(document.body);
        ''')
        # Read through open Shadow DOM; never write a HA state to make this pass.
        assert 'sensor.seminar_latest_purchase_total' in text, 'Receipt sensor not visible on States page'
        assert self.rid in text, 'The received event is not visible on the States page'

    @keyword
    def Filter_Home_Assistant_Demo_Sensors(self):
        # HA 2026.10 uses floating labels outside its nested input Shadow DOM.
        # The inspected States table has Entity, State, Device, Area, Attributes
        # filters in that order; the Set state editor is collapsed.
        inputs = [e for e in self.deep_elements('input') if e.is_displayed()]
        assert len(inputs) == 5, 'States filter layout changed; inspect before selecting the entity filter'
        inputs[0].send_keys('sensor.seminar_')
