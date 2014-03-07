# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2014 Michal Čihař <michal@cihar.com>
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

from django.utils.translation import ugettext_lazy as _
from weblate.trans.checks.base import TargetCheck
from weblate.trans.checks.format import (
    PYTHON_PRINTF_MATCH, PHP_PRINTF_MATCH, C_PRINTF_MATCH,
    PYTHON_BRACE_MATCH,
)
import re

# We ignore some words which are usually not translated
SAME_BLACKLIST = frozenset((
    'accelerator',
    'account',
    'action',
    'actions',
    'active',
    'add-ons',
    'addons',
    'admin',
    'administration',
    'ah',
    'alarm',
    'album',
    'aliasing',
    'alt',
    'amazon',
    'android',
    'antialias',
    'antialiasing',
    'applet',
    'appliance',
    'appliances',
    'aptitude',
    'attribute',
    'attribution',
    'atom',
    'audio',
    'auto',
    'avatar',
    'backend',
    'balance',
    'battery',
    'bb',
    'begin',
    'bios',
    'bit',
    'bitcoin',
    'bitcoins',
    'bitmap',
    'bitmaps',
    'block',
    'blog',
    'bluetooth',
    'bootloader',
    'branch',
    'browser',
    'buffer',
    'byte',
    'bytes',
    'bzip',
    'bzip2',
    'cache',
    'cardinality',
    'chat',
    'click',
    'club',
    'cm',
    'code',
    'collation',
    'color',
    'commit',
    'compression',
    'contact',
    'contacts',
    'context',
    'control',
    'copyright',
    'creation',
    'criteria',
    'csd',
    'csv',
    'ctrl',
    'ctrl+d',
    'ctrl+z',
    'cvs',
    'cyrillic',
    'data',
    'database',
    'date',
    'dbm',
    'debian',
    'debug',
    'default',
    'definition',
    'del',
    'delete',
    'demo',
    'description',
    'design',
    'designer',
    'detail',
    'details',
    'ding',
    'distribution',
    'distro',
    'dm',
    'doc',
    'docs',
    'doctor',
    'document',
    'documentation',
    'download',
    'downloads',
    'dpkg',
    'dpi',
    'drizzle',
    'dummy',
    'dump',
    'e-mail',
    'editor',
    'eib',
    'ellipsis',
    'email',
    'engine',
    'engines',
    'enterprise',
    'error',
    'eu',
    'exchange',
    'expert',
    'export',
    'extra',
    'fanfare',
    'farm',
    'fauna',
    'fax',
    'fedora',
    'feeds',
    'feet',
    'filter',
    'filters',
    'finance',
    'firmware',
    'flash',
    'flattr',
    'flora',
    'font',
    'format',
    'freemind',
    'freeplane',
    'ft',
    'fulltext',
    'function',
    'gammu',
    'general',
    'gentoo',
    'geocache',
    'geocaching',
    'gettext',
    'global',
    'gnu',
    'google',
    'gib',
    'git',
    'gpl',
    'gpx',
    'graphic',
    'graphics',
    'grant',
    'gtk',
    'gzip',
    'hack',
    'hacks',
    'handle',
    'handler',
    'hardware',
    'hashed',
    'headset',
    'help',
    'hmpf',
    'home',
    'homepage',
    'hook',
    'horizontal',
    'host',
    'hosting',
    'hostname',
    'html',
    'http',
    'hut',
    'hyperlink',
    'icon',
    'icons',
    'id',
    'idea',
    'ignore',
    'irc',
    'irda',
    'image',
    'imap',
    'imei',
    'imsi',
    'import',
    'in',
    'inconsistent',
    'index',
    'indigo',
    'info',
    'information',
    'infrastructure',
    'inline',
    'innodb',
    'ins',
    'insert',
    'installation',
    'interlingua',
    'internet',
    'intro',
    'introduction',
    'ion',
    'ios',
    'irix',
    'isbn',
    'ismn',
    'issn',
    'isrc',
    'item',
    'jabber',
    'java',
    'join',
    'joins',
    'jpeg',
    'kernel',
    'kib',
    'km',
    'knoppix',
    'label',
    'land',
    'latex',
    'latin',
    'latitude',
    'layout',
    'ldif',
    'level',
    'login',
    'logo',
    'logos',
    'longitude',
    'lord',
    'libgammu',
    'linestring',
    'link',
    'links',
    'linux',
    'list',
    'lithium',
    'lithium',
    'local',
    'locales',
    'ltr',
    'ma',
    'mah',
    'manager',
    'manual',
    'mailbox',
    'mailboxes',
    'maildir',
    'mailing',
    'markdown',
    'master',
    'max',
    'maximum',
    'media',
    'mediawiki',
    'menu',
    'merge',
    'message',
    'messages',
    'meta',
    'metal',
    'micropayment',
    'micropayments',
    'microsoft',
    'model',
    'module',
    'modules',
    'monitor',
    'motif',
    'mi',
    'mib',
    'mile',
    'min',
    'minimum',
    'mint',
    'minus',
    'minute',
    'mm',
    'multiplayer',
    'musicbottle',
    'mv',
    'n/a',
    'name',
    'namecoin',
    'namecoins',
    'navigation',
    'neutral',
    'nimh',
    'no',
    'node',
    'none',
    'normal',
    'note',
    'notify',
    'nt',
    'null',
    'obex',
    'office',
    'ok',
    'online',
    'opac',
    'open',
    'opendocument',
    'openmaps',
    'openstreet',
    'opensuse',
    'openvpn',
    'opera',
    'operator',
    'option',
    'options',
    'orientation',
    'os',
    'osm',
    'osmand',
    'output',
    'overhead',
    'package',
    'pager',
    'parameter',
    'parameters',
    'partition',
    'party',
    'password',
    'pause',
    'paypal',
    'pdf',
    'pdu',
    'percent',
    'perfume',
    'personal',
    'performance',
    'php',
    'phpmyadmin',
    'pib',
    'pirate',
    'plan',
    'playlist',
    'plugin',
    'plugins',
    'plural',
    'plus',
    'png',
    'po',
    'point',
    'polygon',
    'polymer',
    'pool',
    'port',
    'portable',
    'position',
    'pre',
    'pre-commit',
    'prince',
    'procedure',
    'procedures',
    'process',
    'profiling',
    'program',
    'project',
    'promotion',
    'property',
    'properties',
    'proxy',
    'pt',
    'pull',
    'push',
    'px',
    'python',
    'python-gammu',
    'query',
    'question',
    'questions',
    'realm',
    'rebase',
    'redhat',
    'regexp',
    'relation',
    'relations',
    'replication',
    'repository',
    'report',
    'reports',
    'reset',
    'resource',
    'rich-text',
    'richtext',
    'roadmap',
    'routine',
    'routines',
    'rss',
    'rtl',
    'salt',
    'saver',
    'scalable',
    'scenario',
    'score',
    'screen',
    'screenshot',
    'screensaver',
    'script',
    'scripts',
    'scripting',
    'sergeant',
    'serie',
    'series',
    'server',
    'servers',
    'service',
    'shell',
    'sim',
    'singular',
    'slot',
    'slots',
    'slug',
    'sms',
    'smsc',
    'smsd',
    'snapshot',
    'snapshots',
    'socket',
    'software',
    'solaris',
    'source',
    'spatial',
    'spline',
    'sport',
    'sql',
    'standard',
    'start',
    'status',
    'stop',
    'string',
    'strings',
    'structure',
    'style',
    'submit',
    'subproject',
    'subquery',
    'substring',
    'suggestion',
    'suggestions',
    'sum',
    'sunos',
    'support',
    'suse',
    'svg',
    'symbol',
    'syndication',
    'system',
    'swap',
    'table',
    'tables',
    'tada',
    'tbx',
    'tent',
    'termbase',
    'test',
    'texy',
    'text',
    'thread',
    'threads',
    'tib',
    'timer',
    'todo',
    'todos',
    'total',
    'trigger',
    'triggers',
    'ts',
    'tutorial',
    'tour',
    'type',
    'twiki',
    'twitter',
    'ubuntu',
    'ukolovnik',
    'unicode',
    'unique',
    'unit',
    'update',
    'upload',
    'url',
    'utf',
    'variable',
    'variables',
    'vcalendar',
    'vcard',
    'vector',
    'version',
    'versions',
    'vertical',
    'video',
    'view',
    'views',
    'vote',
    'votes',
    'wammu',
    'web',
    'website',
    'weblate',
    'widget',
    'widgets',
    'wiki',
    'wildcard',
    'windowed',
    'windows',
    'word',
    'www',
    'xhtml',
    'xml',
    'yard',
    'yd',
    'zen',
    'zero',
    'zip',
    'zoom',

    # Months are same in some languages
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
    'july',
    'august',
    'september',
    'october',
    'november',
    'december',

    'jan',
    'feb',
    'mar',
    'apr',
    'jun',
    'jul',
    'aug',
    'sep',
    'oct',
    'nov',
    'dec',

    # Week names shotrcuts
    'mo',
    'tu',
    'we',
    'th',
    'fr',
    'sa',
    'su',

    # Roman numbers
    'ii',
    'iii',
    'iv',
    'vi',

    # Architectures
    'alpha',
    'amd',
    'amd64',
    'arm',
    'aarch',
    'aarch64',
    'hppa',
    'i386',
    'i586',
    'm68k',
    'powerpc',
    'sparc',
    'x86_64',

    # Language names
    'africa',
    'afrikaans',
    'akan',
    'albanian',
    'amharic',
    'arabic',
    'aragonese',
    'armenian',
    'asturian',
    'azerbaijani',
    'basque',
    'belarusian',
    'bengali',
    'bokmål',
    'bosnian',
    'breton',
    'bulgarian',
    'catalan',
    'chinese',
    'cornish',
    'croatian',
    'czech',
    'danish',
    'dutch',
    'dzongkha',
    'english',
    'esperanto',
    'estonian',
    'faroese',
    'filipino',
    'finnish',
    'flemish',
    'french',
    'frisian',
    'friulian',
    'fulah',
    'gaelic',
    'galician',
    'georgian',
    'german',
    'greek',
    'gujarati',
    'gun',
    'haitian',
    'hausa',
    'hebrew',
    'hindi',
    'hungarian',
    'icelandic',
    'india',
    'indonesian',
    'interlingua',
    'irish',
    'italian',
    'japanese',
    'javanese',
    'kannada',
    'kashubian',
    'kazakh',
    'khmer',
    'kirghiz',
    'klingon',
    'korean',
    'kurdish',
    'lao',
    'latvian',
    'limburgish',
    'lingala',
    'lithuanian',
    'luxembourgish',
    'macedonian',
    'maithili',
    'malagasy',
    'malay',
    'malayalam',
    'maltese',
    'maori',
    'mapudungun',
    'marathi',
    'mongolian',
    'morisyen',
    'n\'ko',
    'nahuatl',
    'neapolitan',
    'nepali',
    'norwegian',
    'nynorsk',
    'occitan',
    'oriya',
    'papiamento',
    'pedi',
    'persian',
    'piqad',
    'piemontese',
    'polish',
    'portugal',
    'portuguese',
    'punjabi',
    'pushto',
    'romanian',
    'romansh',
    'russian',
    'scots',
    'serbian',
    'sinhala',
    'slovak',
    'slovenian',
    'somali',
    'songhai',
    'sorani',
    'sotho',
    'spanish',
    'sundanese',
    'swahili',
    'swedish',
    'tajik',
    'tagalog',
    'tamil',
    'tatar',
    'telugu',
    'thai',
    'tibetan',
    'tigrinya',
    'turkish',
    'turkmen',
    'uighur',
    'ukrainian',
    'urdu',
    'uzbek',
    'valencian',
    'venda',
    'vietnamese',
    'walloon',
    'welsh',
    'wolof',
    'yakut',
    'yoruba',
    'zulu',

    # whole alphabet
    'abcdefghijklmnopqrstuvwxyz',
))

# Email address to ignore
EMAIL_RE = re.compile(
    r'[a-z0-9_.-]+@[a-z0-9_.-]+\.[a-z0-9-]{2,}',
    re.IGNORECASE
)

URL_RE = re.compile(
    r'(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)

HASH_RE = re.compile(r'#[A-Za-z0-9_-]*')

DOMAIN_RE = re.compile(
    r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)',
    re.IGNORECASE
)

PATH_RE = re.compile(r'(/[a-zA-Z0-9=:?._-]+)+')

TEMPLATE_RE = re.compile(r'{[a-z_-]+}')

RST_MATCH = re.compile(r'(?::ref:`[^`]+`|``[^`]+``)')


class SameCheck(TargetCheck):
    '''
    Check for not translated entries.
    '''
    check_id = 'same'
    name = _('Not translated')
    description = _('Source and translated strings are same')

    def strip_format(self, msg, flags):
        '''
        Checks whether given string contains only format strings
        and possible punctation. These are quite often not changed
        by translators.
        '''
        if 'python-format' in flags:
            regex = PYTHON_PRINTF_MATCH
        elif 'python-brace-format' in flags:
            regex = PYTHON_BRACE_MATCH
        elif 'php-format' in flags:
            regex = PHP_PRINTF_MATCH
        elif 'c-format' in flags:
            regex = C_PRINTF_MATCH
        elif 'rst-text' in flags:
            regex = RST_MATCH
        else:
            return msg
        stripped = regex.sub('', msg)
        return stripped

    def strip_string(self, msg, flags):
        '''
        Strips (usually) not translated parts from the string.
        '''
        # Strip format strings
        stripped = self.strip_format(msg, flags)

        # Remove email addresses
        stripped = EMAIL_RE.sub('', stripped)

        # Strip full URLs
        stripped = URL_RE.sub('', stripped)

        # Strip hash tags / IRC channels
        stripped = HASH_RE.sub('', stripped)

        # Strip domain names/URLs
        stripped = DOMAIN_RE.sub('', stripped)

        # Strip file/URL paths
        stripped = PATH_RE.sub('', stripped)

        # Strip template markup
        stripped = TEMPLATE_RE.sub('', stripped)

        # Remove some html entities
        stripped = stripped.replace(
            '&nbsp;', ' '
        ).replace(
            '&rsaquo;', '"'
        ).replace(
            '&lt;', '<'
        ).replace(
            '&gt;', '>'
        ).replace(
            '&amp;', '&'
        ).replace(
            '&ldquo;', '"'
        ).replace(
            '&rdquo;', '"'
        ).replace(
            '&times;', '.'
        ).replace(
            '&quot;', '"'
        )

        # Cleanup trailing/leading chars
        stripped = self.strip_chars(stripped)

        # Replace punctation by whitespace for splitting
        stripped = stripped.replace(
            '_', ' '
        ).replace(
            ',', ' '
        ).replace(
            '\\', ' '
        ).replace(
            '/', ' '
        )

        return stripped

    def strip_chars(self, word):
        '''
        Strip chars not useful for translating.
        '''
        return word.strip(
            u' ,./<>?;\'\\:"|[]{}`~!@#$%^&*()-=_+0123456789\n\r✓—'
        )

    def test_word(self, word):
        '''
        Test whether word should be ignored.
        '''
        stripped = self.strip_chars(word)
        return len(stripped) <= 1 or stripped in SAME_BLACKLIST

    def should_ignore(self, source, unit, cache_slot):
        '''
        Check whether given unit should be ignored.
        '''
        # Use cache if available
        result = self.get_cache(unit, cache_slot)
        if result is not None:
            return result

        # Lower case source
        lower_source = source.lower()

        # Check special things like 1:4 1/2 or copyright
        if (len(source.strip('0123456789:/,.')) <= 1
                or '(c) copyright' in lower_source
                or u'©' in source):
            result = True
        else:
            # Strip format strings
            stripped = self.strip_string(lower_source, unit.all_flags)

            # Ignore strings which don't contain any string to translate
            # or just single letter (usually unit or something like that)
            if len(stripped) <= 1:
                result = True
            else:
                # Check if we have any word which is not in blacklist
                # (words which are often same in foreign language)
                result = min(
                    (self.test_word(word) for word in stripped.split())
                )

        # Store in cache
        self.set_cache(unit, result, cache_slot)

        return result

    def check_single(self, source, target, unit, cache_slot):
        # English variants will have most things not translated
        if self.is_language(unit, ('en', )):
            return False

        # One letter things are usually labels or decimal/thousand separators
        if len(source) <= 1 and len(target) <= 1:
            return False

        # Probably shortcut
        if source.isupper() and target.isupper():
            return False

        # Check for ignoring
        if self.should_ignore(source, unit, cache_slot):
            return False

        return source == target
