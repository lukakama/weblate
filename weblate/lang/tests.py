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
Tests for language manipulations.
"""

from django.test import TestCase
from weblate.lang.models import Language
from django.core.management import call_command


class LanguagesTest(TestCase):
    TEST_LANGUAGES = (
        (
            'cs_CZ',
            'cs',
            'ltr',
            '(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2',
        ),
        (
            'cs_CZ@hantec',
            'cs_CZ@hantec',
            'ltr',
            '(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2',
        ),
        (
            'de-DE',
            'de',
            'ltr',
            'n != 1',
        ),
        (
            'de_AT',
            'de_AT',
            'ltr',
            'n != 1',
        ),
        (
            'pt-rBR',
            'pt_BR',
            'ltr',
            'n != 1',
        ),
        (
            'sr_RS@latin',
            'sr_RS@latin',
            'ltr',
            'n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && '
            '(n%100<10 || n%100>=20) ? 1 : 2',
        ),
        (
            'sr-RS@latin',
            'sr_RS@latin',
            'ltr',
            'n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && '
            '(n%100<10 || n%100>=20) ? 1 : 2',
        ),
        (
            'sr_RS_Latin',
            'sr_RS@latin',
            'ltr',
            'n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && '
            '(n%100<10 || n%100>=20) ? 1 : 2',
        ),
        (
            'en_CA_MyVariant',
            'en_CA@myvariant',
            'ltr',
            'n != 1',
        ),
        (
            'en_CZ',
            'en_CZ',
            'ltr',
            'n != 1',
        ),
        (
            'zh_CN',
            'zh_CN',
            'ltr',
            '0',
        ),
        (
            'zh-CN',
            'zh_CN',
            'ltr',
            '0',
        ),
        (
            'zh-CN@test',
            'zh_CN@test',
            'ltr',
            '0',
        ),
        (
            'zh-rCN',
            'zh_CN',
            'ltr',
            '0',
        ),
        (
            'ar',
            'ar',
            'rtl',
            'n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 '
            ': n%100>=11 ? 4 : 5',
        ),
        (
            'ar_AA',
            'ar',
            'rtl',
            'n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 '
            ': n%100>=11 ? 4 : 5',
        ),
        (
            'ar_XX',
            'ar_XX',
            'rtl',
            'n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 '
            ': n%100>=11 ? 4 : 5',
        ),
        (
            'xx',
            'xx',
            'ltr',
            'n != 1',
        ),
    )

    def test_auto_create(self):
        '''
        Tests that auto create correctly handles languages
        '''
        for original, expected, direction, plurals in self.TEST_LANGUAGES:
            # Create language
            lang = Language.objects.auto_get_or_create(original)
            # Check language code
            self.assertEqual(
                lang.code,
                expected,
                'Invalid code for %s' % original
            )
            # Check direction
            self.assertEqual(
                lang.direction,
                direction,
                'Invalid direction for %s' % original
            )
            # Check plurals
            self.assertEqual(
                lang.pluralequation,
                plurals,
                'Invalid plural for %s' % original
            )
            # Check whether html contains both language code and direction
            self.assertIn(direction, lang.get_html())
            self.assertIn(expected, lang.get_html())

    def test_plurals(self):
        '''
        Test whether plural form is correctly calculated.
        '''
        lang = Language.objects.get(code='cs')
        self.assertEqual(
            lang.get_plural_form(),
            'nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;'
        )


class CommandTest(TestCase):
    '''
    Tests for management commands.
    '''
    def test_setuplang(self):
        call_command('setuplang')
        self.assertTrue(Language.objects.exists())

    def test_setuplang_noupdate(self):
        call_command('setuplang', update=False)
        self.assertTrue(Language.objects.exists())
