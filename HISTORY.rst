History
========

0.3.5 (2015-02-15)
-------------------

* Testing deploying to PyPi again, this time will use an annotate tag

0.3.4 (2015-02-15)
-------------------

* Test related changes again (using single instance)
* Also testing deploying to PyPi via Travis

0.3.3 (2014-04-07)
-------------------
* Minor change to a test, setting it as expected failure.

0.3.2 (2014-04-06)
-------------------
* update_note uses utf-8 encoding on returned note content

0.3.1 (2013-12-30)
-------------------
* Minor change to Travis CI PyPi deply details

0.3.0 (2013-12-29)
-------------------
* Change optional argument for get_note_list() to be "since date" instead of quanity
* Various tweaks to tests and CI in attempt to make more robust
* get_note_list() now supports optional tag argument
* get_note() now supports optional version argument
  
0.2.0 (2012-06-02)
-------------------
* Add optional argument for quantity to get_note_list()
* catch HTTPError when fetching notes
* immediately return if note could not be fetched
* trash_note has to succeed for deleting
* add json import fallbacks

0.1.3 (2011-07-17)
-------------------
* fix display of '+' signs

0.1.2 (2011-07-02)
-------------------
* improved documentation
* add sphinx docs

0.1.1 (2011-06-25)
-------------------
* minor changes for pypi

0.1.0 (2011-06-25)
-------------------
* basic API methods
* get note list
* get single note
* add note
* update note
* trash note
* delete note
