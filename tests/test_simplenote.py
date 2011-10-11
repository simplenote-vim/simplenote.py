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
        self.clear_all_notes()
        self.unicode_note = "∮ E⋅da = Q,  n → ∞, ∑ f(i) = ∏ g(i),      ⎧⎡⎛┌─────┐⎞⎤⎫"
        self.unicode_note_key = False
        self.initial_note_count = 0
        self.first_note = False
        self.second_note = False
        note, status = Simplenote(self.user, self.password).add_note("First Note.")
        if status == 0:
            self.initial_note_count += 1
            self.first_note = note['key']
        note, status = Simplenote(self.user, self.password).add_note("Second Note.")
        if status == 0:
            self.initial_note_count += 1
            self.second_note = note['key']
        note, status = Simplenote(self.user, self.password).add_note(self.unicode_note)
        if status == 0:
            self.initial_note_count += 1
            self.unicode_note_key = note['key']

    def tearDown(self):
        self.clear_all_notes()

    def test_simplenote_auth(self):
        token = Simplenote(self.user, self.password).get_token()
        self.assertNotEqual(None, token)

    def test_simplenote_failed_auth(self):
        token = Simplenote(self.user, "").get_token()
        self.assertEqual(None, token)

    def test_simplenote_get_list_length(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        if status == 0:
            self.assertEqual(self.initial_note_count, len(res))
        else:
            self.assertEqual(0, len(res))

    def test_simplenote_get_list_length_25(self):
        for i in xrange(25):
            note, status = Simplenote(self.user, self.password).add_note("Note "+str(i))
            if status == 0:
                self.initial_note_count += 1

        res, status = Simplenote(self.user, self.password).get_note_list()
        if status == 0:
            self.assertEqual(self.initial_note_count, len(res))

    def test_simplenote_limit_list_length_10(self):
        for i in xrange(20):
            note, status = Simplenote(self.user, self.password).add_note("Note "+str(i))
        res, status = Simplenote(self.user, self.password).get_note_list(10)
        if status == 0:
            self.assertEqual(10, len(res))
        else:
            self.assertEqual(0, len(res))

    def test_simplenote_limit_list_length_21(self):
        for i in xrange(25):
            note, status = Simplenote(self.user, self.password).add_note("Note "+str(i))
        res, status = Simplenote(self.user, self.password).get_note_list(21)
        if status == 0:
            self.assertEqual(21, len(res))
        else:
            self.assertEqual(0, len(res))

    def test_simplenote_first_note(self):
        if self.first_note != False:
            note, status = Simplenote(self.user, self.password).get_note(self.first_note)
            if status == 0:
                self.assertTrue(type(note) == dict)
                self.assertEqual("First Note.", note["content"].split('\n')[0])

    def test_simplenote_second_note(self):
        if self.second_note != False:
            note, status = Simplenote(self.user,
                                    self.password).get_note(self.second_note)
            if status == 0:
                self.assertTrue(type(note) == dict)
                self.assertEqual("Second Note.", note["content"].split('\n')[0])

    def test_simplenote_trash_note(self):
        if self.first_note != False:
            note, status = Simplenote(self.user,
                                    self.password).trash_note(self.first_note)
            if status == 0:
                self.assertEqual(1, note["deleted"])

        if self.second_note != False:
            note, status = Simplenote(self.user,
                                    self.password).trash_note(self.second_note)
            if status == 0:
                self.assertEqual(1, note["deleted"])

    def test_simplenote_delete_note(self):
        if self.first_note != False:
            note, status = Simplenote(self.user,
                                    self.password).delete_note(self.first_note)
            if status == 0:
                note, status = Simplenote(self.user,
                                          self.password).get_note(self.first_note)
                self.assertEqual(-1, status)

        if self.second_note != False:
            note, status = Simplenote(self.user,
                                    self.password).delete_note(self.second_note)
            if status == 0:
                note, status = Simplenote(self.user,
                                          self.password).get_note(self.second_note)
                self.assertEqual(-1, status)

    def test_simplenote_add_note_object(self):
        res, status = Simplenote(self.user, self.password).add_note({"content":
                                                                     "new note"})
        if status == 0:
            note, status = Simplenote(self.user, self.password).get_note(res["key"])
            if status == 0:
                self.assertEqual("new note", note["content"])

    def test_simplenote_add_note_content(self):
        res, status = Simplenote(self.user, self.password).add_note("new note")
        if status == 0:
            note, status = Simplenote(self.user, self.password).get_note(res["key"])
            if status == 0:
                self.assertEqual("new note", note["content"])

    def test_simplenote_update_note(self):
        note = {}
        note['key'] = self.first_note
        note["content"] = "Updated Note."
        note, status = Simplenote(self.user, self.password).update_note(note)
        if status == 0:
            note, status = Simplenote(self.user, self.password).get_note(note["key"])
            if status == 0:
                self.assertEqual("Updated Note.", note["content"].split('\n')[0])

    def test_simplenote_is_unicode(self):
        if self.unicode_note_key != False:
            note, status = Simplenote(self.user,
                                    self.password).get_note(self.unicode_note_key)
            if status == 0:
                self.assertTrue(self.is_utf8(note["content"]))

    def test_note_with_plus_signs(self):
        note, status = Simplenote(self.user, self.password).add_note("++")
        if status == 0:
            note, status = Simplenote(self.user, self.password).get_note(note["key"])
            if status == 0:
                self.assertEqual("++", note["content"])

    def is_utf8(self, s):
        try:
            s.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False

    def clear_all_notes(self):
        res, status = Simplenote(self.user, self.password).get_note_list()
        if status == 0:
            [Simplenote(self.user, self.password).delete_note(n["key"]) for n in res]



if __name__ == '__main__':
    unittest.main()


