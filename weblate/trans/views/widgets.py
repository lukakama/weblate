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

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page

from weblate.trans.util import get_site_url
from weblate.trans.models import Project
from weblate.lang.models import Language
from weblate.trans.forms import EnageLanguageForm
from weblate.trans.widgets import WIDGETS
from weblate.trans.views.helper import get_project, try_set_language


def widgets_root(request):
    return render_to_response('widgets-root.html', RequestContext(request, {
        'projects': Project.objects.all_acl(request.user),
    }))


def widgets(request, project):
    obj = get_project(request, project)

    # Parse possible language selection
    form = EnageLanguageForm(obj, request.GET)
    lang = None
    if form.is_valid() and form.cleaned_data['lang'] != '':
        lang = Language.objects.get(code=form.cleaned_data['lang'])

    if lang is None:
        engage_base = reverse('engage', kwargs={'project': obj.slug})
    else:
        engage_base = reverse(
            'engage-lang',
            kwargs={'project': obj.slug, 'lang': lang.code}
        )
    engage_url = get_site_url(engage_base)
    engage_url_track = '%s?utm_source=widget' % engage_url
    widget_base_url = get_site_url(
        reverse('widgets', kwargs={'project': obj.slug})
    )
    widget_list = []
    for widget_name in WIDGETS:
        widget_class = WIDGETS[widget_name]
        color_list = []
        for color in widget_class.colors:
            if lang is None:
                color_url = reverse(
                    'widget-image',
                    kwargs={
                        'project': obj.slug,
                        'widget': widget_name,
                        'color': color,
                    }
                )
            else:
                color_url = reverse(
                    'widget-image-lang',
                    kwargs={
                        'project': obj.slug,
                        'widget': widget_name,
                        'color': color,
                        'lang': lang.code
                    }
                )
            color_list.append({
                'name': color,
                'url': get_site_url(color_url),
            })
        widget_list.append({
            'name': widget_name,
            'colors': color_list,
        })

    return render_to_response('widgets.html', RequestContext(request, {
        'engage_url': engage_url,
        'engage_url_track': engage_url_track,
        'widget_list': widget_list,
        'widget_base_url': widget_base_url,
        'object': obj,
        'image_src': widget_list[0]['colors'][0]['url'],
        'form': form,
    }))


@cache_page(3600)
def render(request, project, widget='287x66', color=None, lang=None):
    obj = get_project(request, project)

    # Handle language parameter
    if lang is not None:
        lang = try_set_language(lang)

    # Get widget class
    try:
        widget_class = WIDGETS[widget]
    except KeyError:
        raise Http404()

    # Construct object
    widget = widget_class(obj, color, lang)

    # Render widget
    widget.render()

    # Get image data
    data = widget.get_image()

    return HttpResponse(content_type='image/png', content=data)
