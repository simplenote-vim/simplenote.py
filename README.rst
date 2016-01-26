==============
simplenote.py
==============

.. image:: https://readthedocs.org/projects/simplenotepy/badge/?version=latest
  :target: http://simplenotepy.readthedocs.org/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://travis-ci.org/mrtazz/simplenote.py.svg?branch=master
    :target: https://travis-ci.org/mrtazz/simplenote.py

.. image:: https://codeclimate.com/github/mrtazz/simplenote.py/badges/gpa.svg
   :target: https://codeclimate.com/github/mrtazz/simplenote.py
   :alt: Code Climate

.. image:: https://readthedocs.org/projects/simplenotepy/badge/?version=latest
:target: http://simplenotepy.readthedocs.org/en/latest/?badge=latest
:alt: Documentation Status

Introduction
=============
simplenote.py is a python library for the simplenote.com_ web service.

Installation
=============
Install via pip::

    pip install simplenote

Or if you must::

    easy_install simplenote


Usage
======
simplenote.py can be imported into any python module::

    import simplenote
    simplenote = simplenote.Simplenote(user, password)

The object then provides the following API methods::

    simplenote.get_note_list(since=YYYY-MM-DD, tags=[])     # Supports optional `since` parameter that takes "YYYY-MM-DD"
                                                            # date string to return only notes modified since this date.
                                                            # Supports optional `tags` parameter that takes a list of tags
                                                            # to return only notes that contain at least one of these tags.

    simplenote.get_note(note_id)                            # note id is value of key `key` in note dict as returned
                                                            # by get_note_list. Supports optional version integer as
                                                            # argument to return previous versions

    simplenote.add_note(note)                               # A ``note`` object is a dictionary with at least a
                                                            # ``content`` property, containing the note text.

    simplenote.update_note(note)                            # The ``update_note`` method needs a note object which
                                                            # also has a ``key`` property.
    simplenote.trash_note(note_id)

    simplenote.delete_note(note_id)


.. _simplenote.com: http://simplenoteapp.com
