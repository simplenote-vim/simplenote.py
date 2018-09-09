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
BUCKET   = 'note'
AUTH_URL = 'https://auth.simperium.com/1/%s/%s' % (APP_ID, BUCKET)
DATA_URL = 'https://api.simperium.com/1/%s/%s' % (APP_ID, BUCKET)
NOTE_FETCH_LENGTH = 1000

class SimplenoteLoginFailed(Exception):
    pass


class Simplenote(object):
    """ Class for interacting with the simplenote web service """

    def __init__(self, token):
        """ object constructor """
        self.header = 'X-Simperium-Token'
        self.token = token

    def get_note(self, noteid, version=None):
        """ method to get a specific note

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
        request.add_header(self.header, self.token)
        try:
            response = urllib2.urlopen(request)
        except HTTPError as e:
            return e, -1
        except IOError as e:
            return e, -1
        note = json.loads(response.read())
        note["key"] = noteid
        note["version"] = int(response.info().getheader("X-Simperium-Version"))
        # py3: response.info()["content-type"]
        # Sort tags
        # For early versions of notes, tags not always available
        if "tags" in note:
            note["tags"] = sorted(note["tags"])

        return note, 0

    def update_note(self, note):
        """ function to update a specific note object, if the note object does not
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
            # set modification timestamp if not set by client
            if 'modifydate' not in note:
                note["modifydate"] = time.time()
        else:
            #Adding a new note
            noteid = uuid.uuid4().hex

        #Strip out version as well?
        if "version" in note:
            note.pop("version", None)
        #Need to add missing dict stuff if missing, might as well do by default, not just for note objects only containing content
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
        for k,v in note_dict.iteritems():
            note.setdefault(k, v)

        url = '%s/i/%s?response=1' % (DATA_URL, noteid)
        # TODO: Could do with being consistent here. Everywhere else is Request(DATA_URL+params)
        request = Request(url, data=json.dumps(note).encode('utf-8'))
        request.add_header(self.header, self.token)
        request.add_header('Content-Type', 'application/json')

        response = ""
        try:
            response = urllib2.urlopen(request)
        except IOError as e:
            return e, -1
        note = json.loads(response.read().decode('utf-8'))
        # Add key back in
        note["key"] = noteid
        note["version"] = int(response.info().getheader("X-Simperium-Version"))
        return note, 0

    def add_note(self, note):
        """wrapper function to add a note

        The function can be passed the note as a dict with the `content`
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

    def get_note_list(self, since=None, tags=[]):
        """ function to get the note list

        The function can be passed optional arguments to limit the
        date range of the list returned and/or limit the list to notes
        containing a certain tag. If omitted a list of all notes
        is returned.

        Arguments:
            - since=YYYY-MM-DD string: only return notes modified
              since this date
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
        params = '/index?limit=%s&data=true' % (str(NOTE_FETCH_LENGTH))
        # if since is not None:
        #    #ISSUE11 - With the Simperium API "since" is a mark and no longer a unix timestamp. So this will have to be removed
        #    try:
        #        sinceUT = time.mktime(datetime.datetime.strptime(since, "%Y-%m-%d").timetuple())
        #        params += '&since=%s' % sinceUT
        #    except ValueError:
        #        pass

        # perform initial HTTP request
        request = Request(DATA_URL+params)
        request.add_header(self.header, self.token)
        try:
            response = urllib2.urlopen(request)
            response_notes = json.loads(response.read())
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

        # get additional notes if bookmark was set in response
        while "mark" in response_notes:
            params += '&mark=%s' % response_notes["mark"]
            if since is not None:
                try:
                    sinceUT = time.mktime(datetime.datetime.strptime(since, "%Y-%m-%d").timetuple())
                    params += '&since=%s' % sinceUT
                except ValueError:
                    pass

            # perform the actual HTTP request
            request = Request(DATA_URL+params)
            request.add_header(self.header, self.token)
            try:
                response = urllib2.urlopen(request)
                response_notes = json.loads(response.read())
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
        # Below based on simplenote.vim, except we return deleted notes as well
        #ISSUE11 - In Simperium index tags are not returned by default so comment this out for now.
        #if (len(tags) > 0):
        #    note_list = [n for n in note_list if (len(set(n["tags"]).intersection(tags)) > 0)]
        return note_list, status

    def trash_note(self, note_id):
        """ method to move a note to the trash

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
        # set deleted property
        note["deleted"] = True
        note["modificationDate"] = time.time()
        # update note
        return self.update_note(note)

    def delete_note(self, note_id):
        """ method to permanently delete a note

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
        request.add_header(self.header, self.token)
        try:
            response = urllib2.urlopen(request)
        except IOError as e:
            return e, -1
        return {}, 0

    def __encode(self, note):
        """ Private method to UTF-8 encode for Python 2

        Arguments:
            A note

        Returns:
            A note

        """

        # Fix the html coding Simplenote introduced
        #if "content" in note:
        #    if sys.version_info < (3, 0):
        #        note["content"] = HTMLParser().unescape(note["content"])
        #    else:
        #        note["content"] = html.unescape(note["content"])

        # Sort tags
        # For early versions of notes, tags not always available
        if "tags" in note:
            note["tags"] = sorted(note["tags"])

        if sys.version_info < (3, 0):
            if "content" in note:
                # use UTF-8 encoding
                note["content"] = note["content"].encode('utf-8')
            # For early versions of notes, tags not always available
            if "tags" in note:
                note["tags"] = [t.encode('utf-8') for t in note["tags"]]
        return note

    def __decode(self, note):
        """ Utility method to UTF-8 decode for Python 2

        Arguments:
            A note

        Returns:
            A note

        """
        if sys.version_info < (3, 0):
            if "content" in note:
                note["content"] = unicode(note["content"], 'utf-8')
            if "tags" in note:
                note["tags"] = [unicode(t, 'utf-8') for t in note["tags"]]
        return note

    def __get_notes(self, notes, params):
        """ Private method to fetch a chunk of notes

        Arguments:
            - Notes
            - URL parameters
            - since date

        Returns:
            - Notes
            - Status

        """

        notes_index = {}

        if self.mark != "mark":
            params += '&mark={0}'.format(self.mark)
        # perform HTTP request
        try:
            request = Request(INDX_URL+params)
            response = urllib2.urlopen(request)
            notes_index = json.loads(response.read().decode('utf-8'))
            notes["data"].extend(notes_index["data"])
            status = 0
        except IOError:
            status = -1
        if "mark" in notes_index:
            self.mark = notes_index["mark"]
        else:
            self.mark = ""
        return notes, status


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
