# -*- coding: utf-8 -*-
"""
    simplenote.py
    ~~~~~~~~~~~~~~

    Python library for accessing the Simplenote API

    :copyright: (c) 2011 by Daniel Schauenberg
    :license: MIT, see LICENSE for more details.
"""
import sys
if sys.version_info > (3, 0):
    import urllib.request as urllib2
    import urllib.error
    from urllib.error import HTTPError
    import urllib.parse as urllib
    import html
else:
    import urllib2
    from urllib2 import HTTPError
    import urllib
    from HTMLParser import HTMLParser

import base64
import time
import datetime
import uuid

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson as json

APP_ID   = 'chalk-bump-f49'
# There is no way for us to hide this key, only obfuscate it.
# So please be kind and don't (ab)use it.
# Simplenote/Simperium didn't have to provide us with this.
API_KEY  = base64.b64decode('YzhjMmI4NjMzNzE1NGNkYWJjOTg5YjIzZTMwYzZiZjQ=')
BUCKET   = 'note'
AUTH_URL = 'https://auth.simperium.com/1/%s/authorize/' % (APP_ID)
DATA_URL = 'https://api.simperium.com/1/%s/%s' % (APP_ID, BUCKET)
NOTE_FETCH_LENGTH = 1000

class SimplenoteLoginFailed(Exception):
    pass


class Simplenote(object):
    """ Class for interacting with the simplenote web service """

    def __init__(self, username, password):
        """ object constructor """
        self.username = username
        self.password = password
        self.header = 'X-Simperium-Token'
        self.token = None
        self.mark = "mark"

    def authenticate(self, user, password):
        """ Method to get simplenote auth token

        Arguments:
            - user (string):     simplenote email address
            - password (string): simplenote password

        Returns:
            Simplenote API token as string
            
        """

        request = Request(AUTH_URL)
        request.add_header('X-Simperium-API-Key', API_KEY)
        if sys.version_info < (3, 3):
            request.add_data(json.dumps({'username': user, 'password': password}))
        else:
            request.data = json.dumps({'username': user, 'password': password}).encode()
        try:
            res = urllib2.urlopen(request).read()
            token = json.loads(res.decode('utf-8'))["access_token"]
        except HTTPError:
            raise SimplenoteLoginFailed('Login to Simplenote API failed!')
        except IOError: # no connection exception
            token = None
        return token

    def get_token(self):
        """ Method to retrieve an auth token.

        The cached global token is looked up and returned if it exists. If it
        is `None` a new one is requested and returned.

        Returns:
            Simplenote API token as string

        """
        if self.token == None:
            self.token = self.authenticate(self.username, self.password)
        try:
            return str(self.token,'utf-8')
        except TypeError:
            return self.token

    def get_note(self, noteid, version=None):
        """ Method to get a specific note

        Arguments:
            - noteid (string): ID of the note to get
            - version (int): optional version of the note to get

        Returns:
            A tuple `(note, status)`

            - note (dict): note object
            - status (int): 0 on sucesss and -1 otherwise

        """
        # request note
        params_version = ""
        if version is not None:
            params_version = '/v/' + str(version)

        params = '/i/%s%s' % (str(noteid), params_version)
        request = Request(DATA_URL+params)
        request.add_header(self.header, self.get_token())
        try:
            response = urllib2.urlopen(request)
        except HTTPError as e:
            return e, -1
        except IOError as e:
            return e, -1
        note = json.loads(response.read().decode('utf-8'))
        note = self.__add_simplenote_api_fields(note, noteid, int(response.info().get("X-Simperium-Version")))
        # Sort tags
        # For early versions of notes, tags not always available
        if "tags" in note:
            note["tags"] = sorted(note["tags"])

        return note, 0

    def update_note(self, note):
        """ Method to update a specific note object, if the note object does not
        have a "key" field, a new note is created

        Arguments
            - note (dict): note object to update

        Returns:
            A tuple `(note, status)`
            - note (dict): note object
            - status (int): 0 on sucesss and -1 otherwise

        """
        # determine whether to create a new note or update an existing one
        # Also need to add/remove key field to keep simplenote.py consistency
        if "key" in note:
            # Then already have a noteid we need to remove before passing to Simperium API
            noteid = note.pop("key", None)
        else:
            # Adding a new note
            noteid = uuid.uuid4().hex


        # TODO: Set a ccid?
        # ccid = uuid.uuid4().hex
        if "version" in note:
            version = note.pop("version", None)
            url = '%s/i/%s/v/%s?response=1' % (DATA_URL, noteid, version)
        else:
            url = '%s/i/%s?response=1' % (DATA_URL, noteid)

        # TODO: Could do with being consistent here. Everywhere else is Request(DATA_URL+params)
        note = self.__remove_simplenote_api_fields(note)
        request = Request(url, data=json.dumps(note).encode('utf-8'))
        request.add_header(self.header, self.get_token())
        request.add_header('Content-Type', 'application/json')

        response = ""
        try:
            response = urllib2.urlopen(request)
        except IOError as e:
            return e, -1
        note = json.loads(response.read().decode('utf-8'))
        note = self.__add_simplenote_api_fields(note, noteid, int(response.info().get("X-Simperium-Version")))
        return note, 0

    def add_note(self, note):
        """ Wrapper method to add a note

        The method can be passed the note as a dict with the `content`
        property set, which is then directly send to the web service for
        creation. Alternatively, only the body as string can also be passed. In
        this case the parameter is used as `content` for the new note.

        Arguments:
            - note (dict or string): the note to add

        Returns:
            A tuple `(note, status)`

            - note (dict): the newly created note
            - status (int): 0 on sucesss and -1 otherwise

        """

        if type(note) == str:
            return self.update_note({"content": note})
        elif (type(note) == dict) and "content" in note:
            return self.update_note(note)
        else:
            return "No string or valid note.", -1

    def get_note_list(self, tags=[]):
        """ Method to get the note list

        The method can be passed optional arguments to limit the
        the list to notes containing a certain tag. If omitted a list
        of all notes is returned.

        Arguments:
            - tags=[] list of tags as string: return notes that have
              at least one of these tags

        Returns:
            A tuple `(notes, status)`

            - notes (list): A list of note objects with all properties set except
            `content`.
            - status (int): 0 on sucesss and -1 otherwise

        """
        # initialize data
        status = 0
        ret = []
        response_notes = {}
        notes = { "index" : [] }

        # get the note index
        # TODO: Using data=false is actually fine with simplenote.vim - sadly no faster though
        params = '/index?limit=%s&data=true' % (str(NOTE_FETCH_LENGTH))

        # perform initial HTTP request
        request = Request(DATA_URL+params)
        request.add_header(self.header, self.get_token())
        try:
            response = urllib2.urlopen(request)
            response_notes = json.loads(response.read().decode('utf-8'))
            # re-write for v1 consistency
            note_objects = []
            for n in response_notes["index"]:
                note_object = self.__add_simplenote_api_fields(n['d'], n['id'], n['v'])
                note_objects.append(note_object)
            notes["index"].extend(note_objects)
        except IOError:
            status = -1

        # get additional notes if bookmark was set in response
        while "mark" in response_notes:
            params += '&mark=%s' % response_notes["mark"]

            # perform the actual HTTP request
            request = Request(DATA_URL+params)
            request.add_header(self.header, self.get_token())
            try:
                response = urllib2.urlopen(request)
                response_notes = json.loads(response.read().decode('utf-8'))
                # re-write for v1 consistency
                note_objects = []
                for n in response_notes["index"]:
                    note_object = n['d']
                    note_object['version'] = n['v']
                    note_object['key'] = n['id']
                    note_objects.append(note_object)
                notes["index"].extend(note_objects)
            except IOError:
                status = -1
        note_list = notes["index"]
        # Can only filter for tags at end, once all notes have been retrieved.
        if (len(tags) > 0):
            note_list = [n for n in note_list if (len(set(n["tags"]).intersection(tags)) > 0)]
        return note_list, status

    def trash_note(self, note_id):
        """ Method to move a note to the trash

        Arguments:
            - note_id (string): key of the note to trash

        Returns:
            A tuple `(note, status)`

            - note (dict): the newly created note or an error message
            - status (int): 0 on sucesss and -1 otherwise

        """
        # get note
        note, status = self.get_note(note_id)
        if (status == -1):
            return note, status
        # set deleted property, but only if not already trashed
        # TODO: A 412 is ok, that's unmodified. Should handle this in update_note and
        # then not worry about checking here
        if not note["deleted"]:
            note["deleted"] = True
            note["modificationDate"] = time.time()
            # update note
            return self.update_note(note)
        else:
            return 0, note

    def delete_note(self, note_id):
        """ Method to permanently delete a note

        Arguments:
            - note_id (string): key of the note to trash

        Returns:
            A tuple `(note, status)`

            - note (dict): an empty dict or an error message
            - status (int): 0 on sucesss and -1 otherwise

        """
        # notes have to be trashed before deletion
        note, status = self.trash_note(note_id)
        if (status == -1):
            return note, status

        params = '/i/%s' % (str(note_id))
        request = Request(url=DATA_URL+params, method='DELETE')
        request.add_header(self.header, self.get_token())
        try:
            response = urllib2.urlopen(request)
        except IOError as e:
            return e, -1
        except HTTPError as e:
            return e, -1
        return {}, 0

    def __add_simplenote_api_fields(self, note, noteid, version):
        # Compatibility with original Simplenote API v2.1.5
        note[u'key'] = noteid
        note[u'version'] = version
        note[u'modifydate'] = note["modificationDate"]
        note[u'createdate'] = note["creationDate"]
        note[u'systemtags'] = note["systemTags"]
        return note

    def __remove_simplenote_api_fields(self, note):
        # These two should have already removed by this point since they are
        # needed for updating, etc, but _just_ incase...
        note.pop("key", None)
        note.pop("version", None)
        # Let's only set these ones if they exist. We don't want None so we can
        # still set defaults afterwards
        mappings = {
                "modifydate": "modificationDate",
                "createdate": "creationDate",
                "systemtags": "systemTags"
        }
        if sys.version_info < (3, 0):
            for k,v in mappings.iteritems():
                if k in note:
                    note[v] = note.pop(k)
        else:
            for k,v in mappings.items():
                if k in note:
                    note[v] = note.pop(k)
        # Need to add missing dict stuff if missing, might as well do by
        # default, not just for note objects only containing content
        createDate = time.time()
        note_dict = {
            "tags" : [],
            "systemTags" : [],
            "creationDate" : createDate,
            "modificationDate" : createDate,
            "deleted" : False,
            "shareURL" : "",
            "publishURL" : "",
        }
        if sys.version_info < (3, 0):
            for k,v in note_dict.iteritems():
                note.setdefault(k, v)
        else:
            for k,v in note_dict.items():
                note.setdefault(k, v)
        return note

class Request(urllib2.Request):
    """ monkey patched version of urllib2's Request to support HTTP DELETE
        Taken from http://python-requests.org, thanks @kennethreitz
    """

    if sys.version_info < (3, 0):
        def __init__(self, url, data=None, headers={}, origin_req_host=None,
                    unverifiable=False, method=None):
            urllib2.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)
            self.method = method

        def get_method(self):
            if self.method:
                return self.method

            return urllib2.Request.get_method(self)
    else:
        pass
