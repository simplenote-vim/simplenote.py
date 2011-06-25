# -*- coding: utf-8 -*-
import unittest
import os
import sys
sys.path.append(os.getcwd())
from simplenote import Simplenote

class TestSimplenote(unittest.TestCase):

    def setUp(self):
        self.user = "simplenote-test@lordofhosts.de"
        self.password = "foobar"
        self.unicode_note = "∮ E⋅da = Q,  n → ∞, ∑ f(i) = ∏ g(i),      ⎧⎡⎛┌─────┐⎞⎤⎫"
        Simplenote(self.user, self.password).add_note("First Note.")
        Simplenote(self.user, self.password).add_note("Second Note.")

    def tearDown(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        [Simplenote(self.user, self.password).delete_note(n["key"]) for n in res]

    def test_simplenote_auth(self):
        token = Simplenote(self.user, self.password).get_token()
        self.assertNotEqual(None, token)

    def test_simplenote_failed_auth(self):
        token = Simplenote(self.user, "").get_token()
        self.assertEqual(None, token)

    def test_simplenote_get_list_length(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        self.assertEqual(2, len(res))

    def test_simplenote_get_list_status(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        self.assertEqual(0, status)

    def test_simplenote_first_note(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        note, status = Simplenote(self.user, self.password).get_note(res[1]["key"])
        self.assertTrue(type(note) == dict)
        self.assertEqual(0, status)
        self.assertEqual("First Note.", note["content"].split('\n')[0])

    def test_simplenote_second_note(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        note, status = Simplenote(self.user, self.password).get_note(res[0]["key"])
        self.assertTrue(type(note) == dict)
        self.assertEqual(0, status)
        self.assertEqual("Second Note.", note["content"].split('\n')[0])

    def test_simplenote_trash_note(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        note, status = Simplenote(self.user, self.password).trash_note(res[0]["key"])
        note, status = Simplenote(self.user, self.password).get_note(res[0]["key"])
        self.assertEqual(0, status)
        self.assertEqual(1, note["deleted"])

    def test_simplenote_delete_note(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        note, status = Simplenote(self.user, self.password).get_note(res[0]["key"])
        # note exists
        self.assertEqual(0, status)
        note, status = Simplenote(self.user, self.password).delete_note(res[0]["key"])
        self.assertEqual({}, note)
        # deletion successful
        self.assertEqual(0, status)
        note, status = Simplenote(self.user, self.password).get_note(res[0]["key"])
        # note does not exist anymore
        self.assertEqual(-1, status)

    def test_simplenote_add_note_object(self):
        res, status = Simplenote(self.user, self.password).add_note({"content":
                                                                     "new note"})
        note, status = Simplenote(self.user, self.password).get_note(res["key"])
        self.assertEqual(0, status)
        self.assertEqual("new note", note["content"])

    def test_simplenote_add_note_content(self):
        res, status = Simplenote(self.user, self.password).add_note("new note")
        note, status = Simplenote(self.user, self.password).get_note(res["key"])
        self.assertEqual(0, status)
        self.assertEqual("new note", note["content"])

    def test_simplenote_update_note(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        note, status = Simplenote(self.user, self.password).get_note(res[0]["key"])
        note["content"] = "Updated Note."
        note, status = Simplenote(self.user, self.password).update_note(note)
        note, status = Simplenote(self.user, self.password).get_note(note["key"])
        self.assertEqual(0, status)
        self.assertEqual("Updated Note.", note["content"].split('\n')[0])

    def test_simplenote_is_unicode(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        note, status = Simplenote(self.user, self.password).get_note(res[0]["key"])
        self.assertTrue(self.is_utf8(note["content"]))

    def test_simplenote_update_unicode(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        note, status = Simplenote(self.user, self.password).get_note(res[0]["key"])
        note["content"] = self.unicode_note
        note, status = Simplenote(self.user, self.password).update_note(note)
        note, status = Simplenote(self.user, self.password).get_note(note["key"])
        self.assertTrue(self.is_utf8(note["content"]))

    def is_utf8(self, s):
        try:
            s.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False


if __name__ == '__main__':
    unittest.main()


