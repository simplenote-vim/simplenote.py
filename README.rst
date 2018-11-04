==============
simplenote.py
==============

.. image:: https://readthedocs.org/projects/simplenotepy/badge/?version=latest
  :target: http://simplenotepy.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://travis-ci.org/mrtazz/simplenote.py.svg?branch=master
    :target: https://travis-ci.org/mrtazz/simplenote.py

.. image:: https://codeclimate.com/github/mrtazz/simplenote.py/badges/gpa.svg
   :target: https://codeclimate.com/github/mrtazz/simplenote.py
   :alt: Code Climate

.. image:: https://img.shields.io/pypi/v/simplenote.svg
   :target: https://pypi.python.org/pypi/simplenote
   :alt: PyPi

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: http://opensource.org/licenses/MIT
   :alt: MIT License

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
    sn = simplenote.Simplenote(user, password)

The object then provides the following API methods::

    sn.get_note_list(data=True, since=cursor, tags=[])  # Supports optional `tags` parameter that takes a list of tags
                                                        # to return only notes that contain at least one of these tags.
                                                        # Also supports a `since` parameter, but as per the Simperium
                                                        # API this is no longer a date, rather a cursor.
                                                        # Lastly, also supports a  `data` parameter (defaults to True)
                                                        # to only return keys/ids and versions

    sn.get_note(note_id)                                # note id is value of key `key` in note dict as returned
                                                        # by get_note_list. Supports optional version integer as
                                                        # argument to return previous versions

    sn.add_note(note)                                   # A ``note`` object is a dictionary with at least a
                                                        # ``content`` property, containing the note text.

    sn.update_note(note)                                # The ``update_note`` method needs a note object which
                                                        # also has a ``key`` property.
    sn.trash_note(note_id)

    simplenote.delete_note(note_id)


.. _simplenote.com: http://simplenoteapp.com
