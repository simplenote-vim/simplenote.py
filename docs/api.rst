.. _api:

===
API
===


.. module:: simplenote

This chapter covers all API interfaces of the simplenote module.

---------------------------------------
Historical Simplenote API - Note Object
---------------------------------------

Prior to the Simperium API a complete note `dict` object contained the
following fields::

    {
      key       : (string, note identifier, created by server),
      deleted   : (bool, whether or not note is in trash),
      modifydate: (last modified date, in seconds since epoch),
      createdate: (note created date, in seconds since epoch),
      syncnum   : (integer, number set by server, track note changes),
      version   : (integer, number set by server, track note content changes),
      minversion: (integer, number set by server, minimum version available for note),
      sharekey  : (string, shared note identifier),
      publishkey: (string, published note identifier),
      systemtags: [(Array of strings, some set by server)],
      tags      : [(Array of strings)],
      content   : (string, data content)
    }

---------------------------
Simperium API - Note Object
---------------------------

Under Simperium some of the fields were renamed and some were removed. String
data also seems to be UTF-8 by default. A Simperium note object looks like
this::


    {
      deleted         : (bool, whether or not note is in trash),
      modificationDate: (last modified date, in seconds since epoch),
      creationDate    : (note created date, in seconds since epoch),
      version         : (integer, number set by server, track note content changes),
      shareURL        : (string, shared url),
      publishURL      : (string, published note url),
      systemTags      : [(Array of strings, some set by server)],
      tags            : [(Array of strings)],
      content         : (string, data content)
    }
   
It no longer includes the "key" (actually now an "id", but still not included
in the note object).

Howver, Simplenote.py tries to work as a drop in replacement for code that
expects the older fields and therefore you can still use the following::

    {
      key       : (string, note identifier, created by server),
      deleted   : (bool, whether or not note is in trash),
      modifydate: (last modified date, in seconds since epoch),
      createdate: (note created date, in seconds since epoch),
      version   : (integer, number set by server, track note content changes),
      systemtags: [(Array of strings, some set by server)],
      tags      : [(Array of strings)],
      content   : (string, data content)
    }

And simplenote.py will handle conversion to/from the Simperium fields.

-----------------------
Simplenote main class
-----------------------


.. autoclass:: Simplenote
   :inherited-members:

