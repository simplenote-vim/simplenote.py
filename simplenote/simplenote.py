# -*- coding: utf-8 -*-
"""
    simplenote.py
    ~~~~~~~~~~~~~~

    Python library for accessing the Simplenote API

    :copyright: (c) 2011 by Daniel Schauenberg
    :license: MIT, see LICENSE for more details.
"""

import urllib2
import base64
import json

AUTH_URL = 'https://simple-note.appspot.com/api/login'
DATA_URL = 'https://simple-note.appspot.com/api2/data'
INDX_URL = 'https://simple-note.appspot.com/api2/index?'
NOTE_FETCH_LENGTH = 20

class Simplenote(object):

    def __init__(self, username, password):
        """ object constructor """
        self.username = urllib2.quote(username)
        self.password = urllib2.quote(password)
        self.token = None

    def authenticate(self, user, password):
        """ function to get simplenote auth token

        Arguments:
        user     -- simplenote email address
        password -- simplenote password

        Returns:
        Simplenote API token

        """
        auth_params = "email=%s&password=%s" % (user, password)
        values = base64.encodestring(auth_params)
        request = Request(AUTH_URL, values)
        try:
            res = urllib2.urlopen(request).read()
            token = urllib2.quote(res)
        except IOError: # no connection exception
            token = None
        return token

    def get_token(self):
        """ function to retrieve an auth token. It returns the cached global
        token or retrieves a new one if there isn't one

        Returns
        the simplenote API token

        """
        if self.token == None:
            self.token = self.authenticate(self.username, self.password)
        return self.token


    def get_note(self, noteid):
        """ function to get a specific note

        Arguments
        noteid -- ID of the note to get

        Returns
        the desired note

        """
        # request note
        params = '/%s?auth=%s&email=%s' % (str(noteid), self.get_token(),
                                           self.username)
        request = Request(DATA_URL+params)
        try:
            response = urllib2.urlopen(request)
        except IOError, e:
            return e, False
        note = json.loads(response.read())
        # use UTF-8 encoding
        note["content"] = note["content"].encode('utf-8')
        note["tags"] = [t.encode('utf-8') for t in note["tags"]]
        return note, True

    def update_note(self, note):
        """ function to update a specific note object, if the note object does not
        have a "key" field, a new note is created

        Arguments
        note  -- note object to update

        Returns
        True and the JSON parsed response on success,
        False with error message otherwise

        """
        # use UTF-8 encoding
        note["content"] = unicode(note["content"], 'utf-8')
        if note.has_key("tags"):
            note["tags"] = [unicode(t, 'utf-8') for t in note["tags"]]

        # determine whether to create a new note or updated an existing one
        if note.has_key("key"):
            url = '%s/%s?auth=%s&email=%s' % (DATA_URL, note["key"],
                                              self.get_token(), self.username)
        else:
            url = '%s?auth=%s&email=%s' % (DATA_URL, self.get_token(), self.username)
        request = Request(url, json.dumps(note))
        response = ""
        try:
            response = urllib2.urlopen(request).read()
        except IOError, e:
            return e, False
        return json.loads(response), True

    def add_note(self, note):
        """wrapper function to add a note

        Arguments
        note -- the note to add

        Returns
        The newly created note and a success status
        """
        pass

    def get_note_list(self):
        """ function to get the note list

        Returns:
        list of note titles and success status

        """
        # initialize data
        status = 0
        ret = []
        response = {}
        notes = { "data" : [] }

        # get the full note index
        params = 'auth=%s&email=%s&length=%s' % (self.get_token(), self.username,
                                                 NOTE_FETCH_LENGTH)
        # perform initial HTTP request
        try:
            request = Request(INDX_URL+params)
            response = json.loads(urllib2.urlopen(request).read())
            notes["data"].extend(response["data"])
        except IOError:
            status = -1

        # get additional notes if bookmark was set in response
        while response.has_key("mark"):
            vals = (self.get_token(), self.username, response["mark"], NOTE_FETCH_LENGTH)
            params = 'auth=%s&email=%s&mark=%s&length=%s' % vals

            # perform the actual HTTP request
            try:
                request = Request(INDX_URL+params)
                response = json.loads(urllib2.urlopen(request).read())
                notes["data"].extend(response["data"])
            except IOError:
                status = -1

        # parse data fields in response
        ret = notes["data"]

        return ret, status

    def trash_note(self, note_id):
        """ function to move a note to the trash

        Arguments
        note_id -- id of the note to trash

        Returns
        list of note titles and success status

        """
        # get note
        note = self.get_note(note_id)
        # set deleted property
        note["deleted"] = 1
        # update note
        return self.update_note(note)

    def delete_note(self, note_id):
        """ function to permanently delete a note

        Arguments:
        note_id -- id of the note to delete

        Returns:
        0 and "OK." on success, -1 and err msg on error

        """
        # notes have to be trashed before deletion
        self.trash_note(note_id)

        params = '/%s?auth=%s&email=%s' % (str(note_id), self.get_token(),
                                           self.username)
        request = Request(url=DATA_URL+params, method='DELETE')
        try:
            res = urllib2.urlopen(request)
        except IOError, e:
            return e, -1
        return {}, 0


class Request(urllib2.Request):
    """ monkey patched version of urllib2's Request to support HTTP DELETE
        Taken from http://python-requests.org, thanks @kennethreitz
    """

    def __init__(self, url, data=None, headers={}, origin_req_host=None,
                unverifiable=False, method=None):
        urllib2.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)
        self.method = method

    def get_method(self):
        if self.method:
            return self.method

        return urllib2.Request.get_method(self)


