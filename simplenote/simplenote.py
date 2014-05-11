# -*- coding: utf-8 -*-
"""
    simplenote.py
    ~~~~~~~~~~~~~~

    Python library for accessing the Simplenote API

    :copyright: (c) 2011 by Daniel Schauenberg
    :license: MIT, see LICENSE for more details.
"""

import urllib
import urllib2
from urllib2 import HTTPError
import base64
import time
import datetime
#ISSUE11 - Option one would be to make simplenote.py a wrapper around the Simperium python library: https://simperium.com/docs/python/
from simperium.core import Auth, Api

APP_ID = "chalk-bump-f49"

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson as json


class SimplenoteLoginFailed(Exception):
    pass


class Simplenote(object):
    """ Class for interacting with the simplenote web service """
    #ISSUE11 - According to Fred Cheng the intention is that users will obtain a token from the Simplenote website. So no username/password auth is required
    def __init__(self, token):
        """ object constructor """
        self.token = token
        self.api = Api(APP_ID, token)


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
        #ISSUE11 - Is error handling required here if at Simperium library level?
        try:
            note = self.api.note.get(noteid, version)
        except HTTPError, e:
            return e, -1
        except IOError, e:
            return e, -1
        #ISSUE11 - Add in noteid as Simperium no longer includes it
        note["key"] = noteid
        # use UTF-8 encoding
        note["content"] = note["content"].encode('utf-8')
        # For early versions of notes, tags not always available
        if note.has_key("tags"):
            note["tags"] = [t.encode('utf-8') for t in note["tags"]]
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
        note["content"] = unicode(note["content"], 'utf-8')
        if "tags" in note:
            note["tags"] = [unicode(t, 'utf-8') for t in note["tags"]]

        # determine whether to create a new note or update an existing one
        #ISSUE11 - But there is no key in note from Simperium so it has to be added when fetched and removed before updating.
        #ISSUE11 - And should it continue to be referenced as "key" as per Simplenote API or switch to "id" as per Simperium API? How much compatibility should be kept?
        if "key" in note:
            #ISSUE11 - Then already have a noteid we need to remove before passing to Simperium API
            noteid = note.pop("key", None)
            note["modificationDate"] = time.time()
            try:
                noteid, note = self.api.note.set(noteid, note, include_response=True)
                #ISSUE11 - And then add back in
                note["key"] = noteid
                status = 0
            except IOError, e:
                return e, -1
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
                note = unicode(note, 'utf-8')

            #ISSUE11 - For Simperium the whole structure is required
            createDate = time.time()
            note = {
                    "tags" : [],
                    "systemTags" : [],
                    "creationDate" : createDate,
                    "modificationDate" : createDate,
                    "deleted" : False,
                    "shareURL" : "",
                    "publishURL" : "",
                    "content" : note
                }
            #ISSUE11 - Need to check for success here
            noteid = self.api.note.new(note)
            note["key"] = noteid
            return note, 0
        #ISSUE11 - Should really check for all required fields, not just content
        elif (type(note) == dict) and "content" in note:
            #ISSUE11 - Need to check for success here
            noteid = self.api.note.new(note)
            note["key"] = noteid
            return note, 0
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
        #ISSUE11 - By default the Simperium API returns just a list of keys/ids and versions. There is an option to return all data, but this will be slower as it includes note content. Need to think what to do.  
        # initialize data
        status = 0
        ret = []
        response = {}
        notes = { "index" : [] }
        since_unix_time = None
        
        if since is not None:
            #ISSUE11 - With the Simperium API "since" is a mark and no longer a unix timestamp. So this will have to be removed
            try:
                since_unix_time = time.mktime(datetime.datetime.strptime(since, "%Y-%m-%d").timetuple())
            except ValueError:
                pass

        # perform initial HTTP request
        try:
            response = self.api.note.index(since=since_unix_time)
            notes["index"].extend(response["index"])
        except IOError:
            status = -1

        # get additional notes if bookmark was set in response
        while "mark" in response:
            mark_response = response["mark"]
            # perform the actual HTTP request
            try:
                response= self.api.note.index(since=since_unix_time,mark=mark_response)
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

    def trash_note(self, noteid):
        """ method to move a note to the trash

        Arguments:
            - noteid (string): key of the note to trash

        Returns:
            A tuple `(note, status)`

            - note (dict): the newly created note or an error message
            - status (int): 0 on sucesss and -1 otherwise

        """
        # set deleted property
        #ISSUE11 - Need try, etc here to return status
        try:
            noteid, note = self.api.note.set(noteid, {"deleted": True, "modificationDate": time.time() }, include_response=True)
            note["key"] = noteid
            status = 0
        except IOError, e:
            return e, -1
        return note, status

    def delete_note(self, noteid):
        """ method to permanently delete a note

        Arguments:
            - noteid (string): key of the note to trash

        Returns:
            A tuple `(note, status)`

            - note (dict): an empty dict or an error message
            - status (int): 0 on sucesss and -1 otherwise

        """
        try:
            self.api.note.delete(noteid)
        except IOError, e:
            return e, -1
        return {}, 0
