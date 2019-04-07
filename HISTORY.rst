History
========

2.1.2 (2019-04-07)
------------------

* Fix error in version number

2.1.1 (2019-04-07)
------------------

* Handle invalid/expired tokens
* Fixed KeyError in get_note_list() when offline
* Fix order of note, status for trash_note

2.1.0 (2018-11-04)
------------------

* Adds since paramter back in (as Simperium cursor, not date)

2.0.3 (2018-10-19)
------------------

* No end facing change in functionality - just removes a superfluous default modificationDate

2.0.2 (2018-10-03)
------------------

* Actually remove the since support like I thought I had. I could have
  re-implemented since in as per tags so it filters after pulling everything
  else, but since (ha!) I used "since" for a faster note loading there seems
  little point.

2.0.1 (2018-10-03)
------------------

* Documentation updatess only

2.0.0 (2018-09-29)
------------------

* Update to the Simperium API: https://simperium.com/docs/http/
* Breaking changes:
  * The since parameter has been removed. Simperium supports the since parameter, but as a cursor, not a date.
  * The syncnum key no longer exists (this is an upstream change)
  * Things seem to be UTF-8 by default
* This should largely be a drop in replacement though: E.g. Simperium uses id instead of key, but simplenote.py handles that for you.

1.0.5 (2018-03-24)
-------------------
* Sort tags in get_note and update_note

1.0.4 (2018-02-26)
-------------------
* Unescape html entites due to api change

1.0.3 (2016-04-03)
-------------------
* Bug fix for an error introduce as a result of code review improvements. 

1.0.2 (2016-03-18)
-------------------
* Code review improvements only. No change to functionality.

1.0.1 (2016-01-13)
-------------------
* I ended up pointing tag v1.0.0 at a re-written commit so need to retag. No changes beyond that.

1.0.0 (2015-11-22)
-------------------
* I think this is stable and proven enough to be version 1 by now. Can then roll into Simplenote.vim v1.

0.4.0 (2015-03-06)
-------------------
* Python 2 and 3 compatibility

0.3.8 (2015-02-16)
-------------------
* Fix version number of deploy, now deploying is working

0.3.7 (2015-02-16)
-------------------
* Testing deploying to PyPi with a change in credentials

0.3.6 (2015-02-15)
-------------------
* Testing deploying to PyPi again, changes to .travis.yml

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
