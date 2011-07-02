.. simplenote.py documentation master file, created by
   sphinx-quickstart on Sat Jun 25 17:40:25 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

simplenote.py: python API wrapper for simplenoteapp.com
=========================================================

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Quickstart
-----------
simplenote.py is a simple wrapper around the simplenoteapp.com web service. It
provides the Simplenote object, with a set of convenience methods to interact
with the service.

First import the module and create an object::

    from simplenote import Simplenote
    simplenote = Simplenote(user, password)

This object then provides the following API methods::

    simplenote.get_noteList()
    simplenote.get_note(note_id)
    simplenote.add_note(note)
    simplenote.update_note(note)
    simplenote.trash_note(note_id)
    simplenote.delete_note(note_id)

A ``note`` object is a dictionary with at least a ``content`` property,
containing the note text. The ``update_note`` method needs a note object which
also has a ``key`` property.



API Reference
-------------

If you are looking for information on a specific function, class or
method, you can most likely find it here.

.. toctree::
   :maxdepth: 2

   api
