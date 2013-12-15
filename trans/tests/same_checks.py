# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2013 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <http://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Tests for quality checks.
"""

from trans.checks.same import (
    SameCheck,
)
from trans.tests.checks import MockUnit, CheckTestCase


class SameCheckTest(CheckTestCase):
    def setUp(self):
        super(SameCheckTest, self).setUp()
        self.check = SameCheck()
        self.test_good_none = ('%(source)s', '%(source)s', 'python-format')
        self.test_good_matching = ('source', 'translation', '')
        self.test_good_ignore = ('alarm', 'alarm', '')
        self.test_failure_1 = ('retezec', 'retezec', '')

    def test_same_english(self):
        self.assertFalse(self.check.check_single(
            'source',
            'source',
            MockUnit(code='en'),
            0
        ))

    def test_same_numbers(self):
        self.do_test(False, ('1:4', '1:4', ''))
        self.do_test(False, ('1, 3, 10', '1, 3, 10', ''))

    def test_same_multi(self):
        self.do_test(
            False,
            (
                u'Linux kernel',
                u'Linux kernel',
                ''
            )
        )
        self.do_test(
            True,
            (
                u'Linux kernel testing image',
                u'Linux kernel testing image',
                ''
            )
        )
        self.do_test(
            False,
            (
                'Gettext (PO)',
                'Gettext (PO)',
                ''
            )
        )
        self.do_test(
            False,
            (
                'powerpc, m68k, i386, amd64',
                'powerpc, m68k, i386, amd64',
                '',
            )
        )

        self.do_test(
            False,
            (
                'Fedora &amp; openSUSE',
                'Fedora &amp; openSUSE',
                '',
            )
        )

    def test_same_copyright(self):
        self.do_test(
            False,
            (
                u'(c) Copyright 2013 Michal Čihař',
                u'(c) Copyright 2013 Michal Čihař',
                ''
            )
        )
        self.do_test(
            False,
            (
                u'© Copyright 2013 Michal Čihař',
                u'© Copyright 2013 Michal Čihař',
                ''
            )
        )

    def test_same_format(self):
        self.do_test(
            False,
            (
                '%d.%m.%Y, %H:%M',
                '%d.%m.%Y, %H:%M',
                'php-format'
            )
        )

        self.do_test(
            True,
            (
                '%d bajt',
                '%d bajt',
                'php-format'
            )
        )

        self.do_test(
            False,
            (
                '%s %s %s %s %s %s &nbsp; %s',
                '%s %s %s %s %s %s &nbsp; %s',
                'c-format',
            )
        )

        self.do_test(
            False,
            (
                '%s %s %s %s %s%s:%s %s ',
                '%s %s %s %s %s%s:%s %s ',
                'c-format'
            )
        )

        self.do_test(
            False,
            (
                '%s%s, %s%s (',
                '%s%s, %s%s (',
                'c-format',
            )
        )

        self.do_test(
            False,
            (
                '%s %s Fax: %s',
                '%s %s Fax: %s',
                'c-format',
            )
        )

        self.do_test(
            False,
            (
                '%i C',
                '%i C',
                'c-format',
            )
        )

    def test_same_rst(self):
        self.do_test(
            False,
            (
                ':ref:`index`',
                ':ref:`index`',
                'rst-text',
            )
        )
        self.do_test(
            True,
            (
                'See :ref:`index`',
                'See :ref:`index`',
                'rst-text',
            )
        )
        self.do_test(
            False,
            (
                '``mysql``',
                '``mysql``',
                'rst-text',
            )
        )
        self.do_test(
            True,
            (
                'Use ``mysql`` module',
                'Use ``mysql`` module',
                'rst-text',
            )
        )

    def test_same_email(self):
        self.do_test(
            False,
            (
                'michal@cihar.com',
                'michal@cihar.com',
                ''
            )
        )
        self.do_test(
            True,
            (
                'Please contact michal@cihar.com',
                'Please contact michal@cihar.com',
                ''
            )
        )

    def test_same_url(self):
        self.do_test(
            False,
            (
                'http://weblate.org/',
                'http://weblate.org/',
                ''
            )
        )
        self.do_test(
            True,
            (
                'Please see http://weblate.org/',
                'Please see http://weblate.org/',
                ''
            )
        )
        self.do_test(
            False,
            (
                '[2]: http://code.google.com/p/pybluez/',
                '[2]: http://code.google.com/p/pybluez/',
                ''
            )
        )
        self.do_test(
            False,
            (
                '[2]: https://sourceforge.net/projects/pywin32/',
                '[2]: https://sourceforge.net/projects/pywin32/',
                ''
            )
        )

    def test_same_channel(self):
        self.do_test(
            False,
            (
                '#weblate',
                '#weblate',
                ''
            )
        )
        self.do_test(
            True,
            (
                'Please use #weblate',
                'Please use #weblate',
                ''
            )
        )

    def test_same_domain(self):
        self.do_test(
            False,
            (
                'weblate.org',
                'weblate.org',
                ''
            )
        )
        self.do_test(
            False,
            (
                'demo.weblate.org',
                'demo.weblate.org',
                ''
            )
        )
        self.do_test(
            False,
            (
                '#weblate @ irc.freenode.net',
                '#weblate @ irc.freenode.net',
                ''
            )
        )
        self.do_test(
            True,
            (
                'Please see demo.weblate.org',
                'Please see demo.weblate.org',
                ''
            )
        )

    def test_same_path(self):
        self.do_test(
            False,
            (
                '/cgi-bin/koha/catalogue/search.pl?q=',
                '/cgi-bin/koha/catalogue/search.pl?q=',
                ''
            )
        )
        self.do_test(
            True,
            (
                'File/directory',
                'File/directory',
                ''
            )
        )

    def test_same_template(self):
        self.do_test(
            False,
            (
                '{building}: {description}',
                '{building}: {description}',
                ''
            )
        )
        self.do_test(
            True,
            (
                '{building}: some description',
                '{building}: some description',
                ''
            )
        )

    def test_same_lists(self):
        self.do_test(
            False,
            (
                'a.,b.,c.,d.',
                'a.,b.,c.,d.',
                ''
            )
        )
        self.do_test(
            False,
            (
                'i.,ii.,iii.,iv.',
                'i.,ii.,iii.,iv.',
                ''
            )
        )
