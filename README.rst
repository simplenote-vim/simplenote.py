==============
simplenote.py
==============

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

    from simplenote import Simplenote
    simplenote = Simplenote(user, password)

The object then provides the following API methods::

    simplenote.get_note_list()          # Supports optional "YYYY-MM-DD" date string as argument
                                        # to return only notes modified since this date

    simplenote.get_note(note_id)        # note id is value of key `key` in note dict as returned 
                                        # by get_note_list. Supports optional version integer as
                                        # argument to return previous versions

    simplenote.add_note(note)           # A ``note`` object is a dictionary with at least a 
                                        # ``content`` property, containing the note text.

    simplenote.update_note(note)        # The ``update_note`` method needs a note object which
                                        # also has a ``key`` property.
    simplenote.trash_note(note_id)
    
    simplenote.delete_note(note_id)

 

Meta
======
* `Bugs <https://github.com/mrtazz/simplenote.py/issues>`_
* `Continuous Integration <http://travis-ci.org/#!/mrtazz/simplenote.py>`_
* `Docs <http://readthedocs.org/docs/simplenotepy/en/latest/api.html>`_

Contribute
===========
If you want to contribute:

* Fork the project.
* Make your feature addition or bug fix based on master.
* Add tests for it. This is important so I don’t break it in a future version unintentionally.
* Commit, do not mess with version
* Send me a pull request. Bonus points for topic branches.

.. _simplenote.com: http://simplenoteapp.com
