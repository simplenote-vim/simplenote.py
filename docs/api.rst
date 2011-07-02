.. _api:

===
API
===


.. module:: simplenote

This chapter covers all API interfaces of the simplenote module.

-------------------
Basic Note Object
-------------------

All notes are handled as `dict` objects in simplenote.py. A complete note
contains the following properties::

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

-----------------------
Simplenote main class
-----------------------


.. autoclass:: Simplenote
   :inherited-members:

