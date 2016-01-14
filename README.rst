==============
simplenote.py
==============

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


Contribute
===========
If you want to contribute:

* Fork the project.
* Make your feature addition or bug fix based on master.
* Run the tests (See below).
* Add tests for your feature if you can and it appropriate. This is important so I don’t break it in a future version unintentionally.
* Commit, do not mess with version.
* Send me a pull request, let me know what tests fail as a result of the changes.


Tests
======
Before making a pull request or sending a patch it is recommended you run the tests against the most recent version of Python 2 and Python 3. I.e::

    python27 tests/test_simplenote.py

and::

    python34 tests/test_simplenote.py


Meta
======
* `Bugs <https://github.com/mrtazz/simplenote.py/issues>`_
* `Continuous Integration <http://travis-ci.org/#!/mrtazz/simplenote.py>`_
* `Docs <http://readthedocs.org/docs/simplenotepy/en/latest/api.html>`_

.. _simplenote.com: http://simplenoteapp.com
