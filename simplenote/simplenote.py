# -*- coding: utf-8 -*-
"""
    simplenote.py
    ~~~~~~~~~~~~~~

    Python library for accessing the Simplenote API

    :copyright: (c) 2011 by Daniel Schauenberg
    :license: MIT, see LICENSE for more details.
"""

#ISSUE11 - Option two would be to use the simperium http api directly: https://simperium.com/docs/reference/http/
import urllib
import urllib2
from urllib2 import HTTPError
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
#ISSUE11 - This can increase now
NOTE_FETCH_LENGTH = 1000

class SimplenoteLoginFailed(Exception):
    pass


class Simplenote(object):
    """ Class for interacting with the simplenote web service """

    def __init__(self, token):
        """ object constructor """
        self.header = 'X-Simperium-Token'
        self.token = token
        #ISSUE11 - According to Fred Cheng the intention is that users will obtain a token from the Simplenote website. So no username/password auth is required; more evidence for that here: http://stackoverflow.com/a/22773475/208793


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
        except HTTPError, e:
            return e, -1
        except IOError, e:
            return e, -1
        note = json.loads(response.read())
        # use UTF-8 encoding
        #ISSUE11 - I think UTF-8 encoding is used by default now anyway? So removed that bit of code
        #ISSUE11 - Add in noteid as Simperium no longer includes it
        note["key"] = noteid
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
        # use UTF-8 encoding
        #ISSUE11 - But only conditionally, don't try to encode everything
        if (type(note["content"]) == str):
            note["content"] = unicode(note["content"], 'utf-8')
        #ISSUE11 - And should probably should do the same conditionally here
        if "tags" in note:
            note["tags"] = [unicode(t, 'utf-8') for t in note["tags"]]

        # determine whether to create a new note or updated an existing one
        if "key" in note:
            #ISSUE11 - Then already have a noteid we need to remove before passing to Simperium API
            noteid = note.pop("key", None)
            #ISSUE11 - Missed this conditional from the simperium-lib branch
            # set modification timestamp if not set by client
            if 'modificationDate' not in note:
                note["modificationDate"] = time.time()

            url = '%s/i/%s?response=1' % (DATA_URL, noteid)
            #ISSUE11 - Could do with being consistent here. Everywhere else is Request(DATA_URL+params)
            request = Request(url, data=json.dumps(note))
            request.add_header(self.header, self.token)
            #ISSUE11 - Below not required, but good practice
            request.add_header('Content-Type', 'application/json')

            response = ""
            try:
                response = urllib2.urlopen(request)
            except IOError, e:
                return e, -1
            note = json.loads(response.read())
            #ISSUE11 - Add key back in
            note["key"] = noteid
            status = 0
        else:
            #ISSUE11 - If creating new, assume doesn't have the required full Simperium structure and pass just content string to add_note
            note, status = self.add_note(note["content"])
        return note, status

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

        if (type(note) == str) or (type(note) == unicode):
            if type(note) == str:
                # use UTF-8 encoding
                note_content = unicode(note, 'utf-8')

            #ISSUE11 - For Simperium the whole structure is required
            createDate = time.time()
            note_dict = {
                    "tags" : [],
                    "systemTags" : [],
                    "creationDate" : createDate,
                    "modificationDate" : createDate,
                    "deleted" : False,
                    "shareURL" : "",
                    "publishURL" : "",
                    "content" : note_content
                }
        elif (type(note) == dict) and "content" in note:
            pass
        else:
            return "No string or valid note.", -1

        #ISSUE11 - Under Simperium API must generate our own ID.
        noteid = uuid.uuid4().hex
        url = '%s/i/%s?response=1' % (DATA_URL, noteid)
        #ISSUE11 - Could do with being consistent here. Everywhere else is Request(DATA_URL+params)
        request = Request(url, data=json.dumps(note_dict))
        request.add_header(self.header, self.token)
        #ISSUE11 - Below not required, but good practice
        request.add_header('Content-Type', 'application/json')

        response = ""
        try:
            response = urllib2.urlopen(request)
        #ISSUE 11 - Why no http error here? Consistency
        except IOError, e:
            return e, -1
        note = json.loads(response.read())
        note["key"] = noteid
        return note, 0

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
        params = '/index?limit=%s' % (str(NOTE_FETCH_LENGTH))
        if since is not None:
            #ISSUE11 - With the Simperium API "since" is a mark and no longer a unix timestamp. So this will have to be removed
            try:
                sinceUT = time.mktime(datetime.datetime.strptime(since, "%Y-%m-%d").timetuple())
                params += '&since=%s' % sinceUT
            except ValueError:
                pass

        # perform initial HTTP request
        request = Request(DATA_URL+params)
        request.add_header(self.header, self.token)
        try:
            response = urllib2.urlopen(request)
            #ISSUE11 - Trying to be a bit more consistent with things
            response_notes = json.loads(response.read())
            notes["index"].extend(response_notes["index"])
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
            try:
                response = urllib2.urlopen(request)
                response_notes = json.loads(response.read())
                notes["index"].extend(response["index"])
            except IOError:
                status = -1

        # parse data fields in response
        note_list = notes["index"]

        # Can only filter for tags at end, once all notes have been retrieved.
        #Below based on simplenote.vim, except we return deleted notes as well
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
        #ISSUE11 - Missed the below from simperium-lib option
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


