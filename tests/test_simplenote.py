# -*- coding: utf-8 -*-
import unittest
import os
import sys
sys.path.append(os.getcwd())
#Override NOTE_FETCH_LENGTH for testing purposes
import simplenote
simplenote.simplenote.NOTE_FETCH_LENGTH = 5

class TestSimplenote(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = "simplenote-test@lordofhosts.de"
        password = "foobar"
        cls.simplenote_instance = simplenote.Simplenote(cls.user, password)

    def setUp(self):
        self.clear_all_notes()
        self.unicode_note = "∮ E⋅da = Q,  n → ∞, ∑ f(i) = ∏ g(i),      ⎧⎡⎛┌─────┐⎞⎤⎫"
        self.unicode_note_key = False
        self.initial_note_count = 0
        self.tag_note_count = 0
        self.first_note = False
        self.second_note = False
        note, status = self.simplenote_instance.add_note({"content": "First Note.", "tags": ["tag1"]})
        if status == 0:
            self.initial_note_count += 1
            self.tag_note_count += 1
            self.first_note = note['key']
        note, status = self.simplenote_instance.add_note({"content": "Second Note.", "tags": ["tag1", "tag2"]})
        if status == 0:
            self.initial_note_count += 1
            self.tag_note_count += 1
            self.second_note = note['key']
        note, status = self.simplenote_instance.add_note(self.unicode_note)
        if status == 0:
            self.initial_note_count += 1
            self.unicode_note_key = note['key']

    def tearDown(self):
        self.clear_all_notes()

    def test_simplenote_auth(self):
        token = self.simplenote_instance.get_token()
        self.assertNotEqual(None, token)

    def test_simplenote_failed_auth(self):
        s = simplenote.Simplenote(self.user, "")
        self.assertRaises(simplenote.SimplenoteLoginFailed, s.get_token)

    def test_simplenote_get_list_length(self):
        res, status = self.simplenote_instance.get_note_list()
        if status == 0:
            self.assertEqual(self.initial_note_count, len(res))
        else:
            self.assertEqual(0, len(res))

    def test_simplenote_get_list_length_longer_than_note_fetch_length(self):
        while self.initial_note_count <= simplenote.simplenote.NOTE_FETCH_LENGTH+1:
            note, status = self.simplenote_instance.add_note("Note "+str(self.initial_note_count+1))
            if status == 0:
                self.initial_note_count += 1

        res, status = self.simplenote_instance.get_note_list()
        if status == 0:
            self.assertTrue(len(res) > simplenote.simplenote.NOTE_FETCH_LENGTH)

    def test_simplenote_get_list_with_tags(self):
        res, status = self.simplenote_instance.get_note_list(tags=["tag1"])
        if status == 0:
            self.assertEqual(self.tag_note_count, len(res))
        else:
            self.assertEqual(0, len(res))

    def test_simplenote_first_note(self):
        if self.first_note != False:
            note, status = self.simplenote_instance.get_note(self.first_note)
            if status == 0:
                self.assertTrue(type(note) == dict)
                self.assertEqual("First Note.", note["content"].split('\n')[0])

    def test_simplenote_second_note(self):
        if self.second_note != False:
            note, status = self.simplenote_instance.get_note(self.second_note)
            if status == 0:
                self.assertTrue(type(note) == dict)
                self.assertEqual("Second Note.", note["content"].split('\n')[0])

    def test_simplenote_trash_note(self):
        if self.first_note != False:
            note, status = self.simplenote_instance.trash_note(self.first_note)
            if status == 0:
                self.assertEqual(1, note["deleted"])

        if self.second_note != False:
            note, status = self.simplenote_instance.trash_note(self.second_note)
            if status == 0:
                self.assertEqual(1, note["deleted"])

    def test_simplenote_delete_note(self):
        if self.first_note != False:
            note, status = self.simplenote_instance.delete_note(self.first_note)
            if status == 0:
                note, status = self.simplenote_instance.get_note(self.first_note)
                self.assertEqual(-1, status)

        if self.second_note != False:
            note, status = self.simplenote_instance.delete_note(self.second_note)
            if status == 0:
                note, status = self.simplenote_instance.get_note(self.second_note)
                self.assertEqual(-1, status)

    def test_simplenote_add_note_object(self):
        res, status = self.simplenote_instance.add_note({"content":
                                                                     "new note"})
        if status == 0:
            note, status = self.simplenote_instance.get_note(res["key"])
            if status == 0:
                self.assertEqual("new note", note["content"])

    def test_simplenote_add_note_content(self):
        res, status = self.simplenote_instance.add_note("new note")
        if status == 0:
            note, status = self.simplenote_instance.get_note(res["key"])
            if status == 0:
                self.assertEqual("new note", note["content"])

    def test_simplenote_update_note(self):
        note = {}
        note['key'] = self.first_note
        note["content"] = "Updated Note."
        note, status = self.simplenote_instance.update_note(note)
        if status == 0:
            note, status = self.simplenote_instance.get_note(note["key"])
            if status == 0:
                self.assertEqual("Updated Note.", note["content"].split('\n')[0])

    def test_simplenote_is_unicode(self):
        if self.unicode_note_key != False:
            note, status = self.simplenote_instance.get_note(self.unicode_note_key)
            if status == 0:
                self.assertTrue(self.is_utf8(note["content"]))

    def test_note_with_plus_signs(self):
        note, status = self.simplenote_instance.add_note("++")
        if status == 0:
            note, status = self.simplenote_instance.get_note(note["key"])
            if status == 0:
                self.assertEqual("++", note["content"])

    def test_note_get_previous_version(self):
        note_v1, status = self.simplenote_instance.add_note("Hello")
        if status == 0:
            note_v2 = {}
            note_v2['key'] = note_v1["key"]
            note_v2["content"] = "Goodbye"
            note_v2, status = self.simplenote_instance.update_note(note_v2)
            if status == 0:
                if note_v2["version"] > 1:
                    note, status = self.simplenote_instance.get_note(note_v2["key"], note_v2["version"]-1)
                    if status == 0:
                        self.assertEqual("Hello", note["content"])

    def is_utf8(self, s):
        if sys.version_info < (3, 0):
            try:
                s.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
        else:
           return s == self.unicode_note


    def clear_all_notes(self):
        res, status = self.simplenote_instance.get_note_list()
        while (len(res) > 0) and (status == 0):
            [self.simplenote_instance.delete_note(n["key"]) for n in res]
            res, status = self.simplenote_instance.get_note_list()

if __name__ == '__main__':
    unittest.main()
