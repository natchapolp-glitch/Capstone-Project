"""Delivery means both HA sensor values match the confirmed payload."""
import unittest

from receipt_lab.preboard.profile_transport import check_states, ENTITIES


class HAValueTests(unittest.TestCase):
    def test_total_and_item_count_are_both_checked_including_missing_total(self):
        extraction={'grand_total':10,'items':[{'name':'synthetic item'},{'name':'synthetic item'}]}
        states=[{'entity_id':ENTITIES[0],'state':'10.0'},{'entity_id':ENTITIES[1],'state':'2'}]
        self.assertTrue(check_states(states,extraction))
        states[0]['state']='99'
        self.assertFalse(check_states(states,extraction))
        states[0]['state']='10';states[1]['state']='3'
        self.assertFalse(check_states(states,extraction))
        self.assertFalse(check_states(states[:1],extraction))
        states[0]['state']='unknown';states[1]['state']='2';extraction['grand_total']=None
        self.assertTrue(check_states(states,extraction))


if __name__=='__main__':unittest.main()
