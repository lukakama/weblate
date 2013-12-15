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
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.template import RequestContext
from django.core.urlresolvers import reverse
from weblate.lang.models import Language
from weblate.trans.models import Project, Dictionary, Change
from urllib import urlencode


def show_languages(request):
    return render_to_response('languages.html', RequestContext(request, {
        'languages': Language.objects.have_translation(),
        'title': _('Languages'),
    }))


def show_language(request, lang):
    obj = get_object_or_404(Language, code=lang)
    last_changes = Change.objects.filter(
        translation__language=obj
    ).order_by('-timestamp')[:10]
    dicts = Dictionary.objects.filter(
        language=obj
    ).values_list('project', flat=True).distinct()

    return render_to_response('language.html', RequestContext(request, {
        'object': obj,
        'last_changes': last_changes,
        'last_changes_rss': reverse('rss-language', kwargs={'lang': obj.code}),
        'last_changes_url': urlencode({'lang': obj.code}),
        'dicts': Project.objects.all_acl(request.user).filter(id__in=dicts),
    }))
