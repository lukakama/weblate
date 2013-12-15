.. _api:

Weblate's Web API
=================

.. _hooks:

Notification hooks
------------------

Notification hooks allow external applications to notify Weblate that Git
repository has been updated.

.. describe:: GET /hooks/update/(string:project)/(string:subproject)/

   Triggers update of a subproject (pulling from Git and scanning for
   translation changes).

.. describe:: GET /hooks/update/(string:project)/

   Triggers update of all subprojects in a project (pulling from Git and
   scanning for translation changes).

.. describe:: POST /hooks/github/

    Special hook for handling GitHub notifications and automatically updating
    matching subprojects.

    .. note::

        GitHub includes direct support for notifying Weblate, just enable
        Weblate service hook in repository settings and set URL to URL of your
        Weblate installation.

    .. seealso:: http://help.github.com/post-receive-hooks/ :setting:`ENABLE_HOOKS`

.. describe:: POST /hooks/bitbucket/

    Special hook for handling Bitbucket notifications and automatically
    updating matching subprojects.

    .. seealso:: https://confluence.atlassian.com/display/BITBUCKET/POST+Service+Management https://confluence.atlassian.com/display/BITBUCKET/Writing+Brokers+for+Bitbucket :setting:`ENABLE_HOOKS`

.. _exports:

Exports
-------

Weblate provides various exports to allow you further process the data.

.. describe:: GET /exports/stats/(string:project)/(string:subproject)/

    Retrieves statistics for given subproject in JSON format.

    You can get pretty-printed output by appending ``?indent=1`` to the
    request.

    Example response:

    .. code-block:: json

        [
            {
                "code": "cs", 
                "failing": 0, 
                "failing_percent": 0.0, 
                "fuzzy": 0, 
                "fuzzy_percent": 0.0, 
                "last_author": "Michal \u010ciha\u0159",
                "last_change": "2012-03-28T15:07:38+00:00",
                "name": "Czech", 
                "total": 436, 
                "translated": 436, 
                "translated_percent": 100.0, 
                "url": "http://l10n.cihar.com/engage/weblate/cs/"
                "url_translate": "http://l10n.cihar.com/projects/weblate/master/cs/"
            }, 
            {
                "code": "nl", 
                "failing": 21, 
                "failing_percent": 4.8, 
                "fuzzy": 11, 
                "fuzzy_percent": 2.5, 
                "last_author": null,
                "last_change": null,
                "name": "Dutch", 
                "total": 436, 
                "translated": 319, 
                "translated_percent": 73.2, 
                "url": "http://l10n.cihar.com/engage/weblate/nl/"
                "url_translate": "http://l10n.cihar.com/projects/weblate/master/nl/"
            }, 
            {
                "code": "el", 
                "failing": 11, 
                "failing_percent": 2.5, 
                "fuzzy": 21, 
                "fuzzy_percent": 4.8, 
                "last_author": null,
                "last_change": null,
                "name": "Greek", 
                "total": 436, 
                "translated": 312, 
                "translated_percent": 71.6, 
                "url": "http://l10n.cihar.com/engage/weblate/el/"
                "url_translate": "http://l10n.cihar.com/projects/weblate/master/el/"
            }, 
        ]

    Included data:

    ``code``
        language code
    ``failing``, ``failing_percent``
        number and percentage of failing checks
    ``fuzzy``, ``fuzzy_percent``
        number and percentage of fuzzy strings
    ``last_author``
        name of last author
    ``last_change``
        date of last change
    ``name``
        language name
    ``total``
        total number of strings
    ``translated``, ``translated_percet``
        number and percentage of translated strings
    ``url``
        URL to access the translation (engagement URL)
    ``url_translate``
        URL to access the translation (real translation URL)

.. _rss:

RSS feeds
---------

Changes in translations are exported in RSS feeds.

.. describe:: GET /exports/rss/(string:project)/(string:subproject)/(string:language)/

    Retrieves RSS feed with recent changes for a translation.

.. describe:: GET /exports/rss/(string:project)/(string:subproject)/

    Retrieves RSS feed with recent changes for a subproject.

.. describe:: GET /exports/rss/(string:project)/

    Retrieves RSS feed with recent changes for a project.

.. describe:: GET /exports/rss/language/(string:language)/

    Retrieves RSS feed with recent changes for a language.

.. describe:: GET /exports/rss/

    Retrieves RSS feed with recent changes for Weblate instance.

.. seealso:: https://en.wikipedia.org/wiki/RSS
