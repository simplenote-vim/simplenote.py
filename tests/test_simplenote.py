# encoding: utf-8
import unittest
import os
import sys
sys.path.append(os.getcwd())
from simplenote import Simplenote

class TestNotifyUser(unittest.TestCase):

    def setUp(self):
        self.user = "test_provider"
        self.password = "test_user"

    def test_simplenote_get_list_length(self):
        res = Simplenote(self.user, self.password).get_note_list()
        self.assertEqual(2, len(res))

    def test_simplenote_first_note(self):
        pass

    def test_simplenote_second_note(self):
        pass

    def test_simplenote_trash_note(self):
        pass

    def test_simplenote_delete_note(self):
        pass

    def test_simplenote_add_note(self):
        pass

    def test_simplenote_update_note(self):
        pass

    def test_simplenote_is_utf8(self):
        pass

    def test_simplenote_update_utf8(self):
        pass

if __name__ == '__main__':
    unittest.main()
