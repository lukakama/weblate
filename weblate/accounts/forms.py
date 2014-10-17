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

from django import forms
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.auth.forms import AuthenticationForm

from weblate.accounts.models import Profile, VerifiedEmail
from weblate.accounts.captcha import MathCaptcha
from weblate.lang.models import Language
from weblate.trans.models import Project
from django.contrib.auth.models import User
from django.utils.encoding import force_unicode
from itertools import chain
import unicodedata
import weblate

try:
    import icu  # pylint: disable=import-error
    HAS_ICU = True
except ImportError:
    HAS_ICU = False


def remove_accents(input_str):
    """
    Removes accents from a string.
    """
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii


def sort_choices(choices):
    '''
    Sorts choices alphabetically.

    Either using cmp or ICU.
    '''
    if not HAS_ICU:
        return sorted(
            choices,
            key=lambda tup: remove_accents(tup[1])
        )
    else:
        locale = icu.Locale(get_language())
        collator = icu.Collator.createInstance(locale)
        return sorted(
            choices,
            key=lambda tup: tup[1],
            cmp=collator.compare
        )


class NoStripEmailField(forms.EmailField):
    """
    Email field which does no stripping.
    """
    def clean(self, value):
        value = self.to_python(value)
        # We call super-super method to skip default EmailField behavior
        # pylint: disable=E1003
        return super(forms.EmailField, self).clean(value)


class UsernameField(forms.RegexField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 30
        kwargs['min_length'] = 5
        kwargs['regex'] = r'^[\w.@+-]+$'
        kwargs['help_text'] = _('At least five characters long.')
        kwargs['label'] = _('Username')
        kwargs['error_messages'] = {
            'invalid': _(
                'This value may contain only letters, '
                'numbers and following characters: @ . + - _'
            )
        }
        kwargs['required'] = True
        self.valid = None

        super(UsernameField, self).__init__(*args, **kwargs)

    def clean(self, value):
        '''
        Username validation, requires length of five chars and unique.
        '''
        if value is not None:
            existing = User.objects.filter(
                username__iexact=value
            )
            if existing.exists() and value != self.valid:
                raise forms.ValidationError(
                    _(
                        'This username is already taken. '
                        'Please choose another.'
                    )
                )

        return super(UsernameField, self).clean(value)


class SortedSelectMixin(object):
    '''
    Mixin for Select widgets to sort choices alphabetically.
    '''
    def render_options(self, choices, selected_choices):
        '''
        Renders sorted options.
        '''
        # Normalize to strings.
        selected_choices = set(force_unicode(v) for v in selected_choices)
        output = []

        # Actually sort values
        all_choices = sort_choices(list(chain(self.choices, choices)))

        # Stolen from Select.render_options
        for option_value, option_label in all_choices:
            output.append(
                self.render_option(
                    selected_choices, option_value, option_label
                )
            )
        return u'\n'.join(output)


class SortedSelectMultiple(SortedSelectMixin, forms.SelectMultiple):
    '''
    Wrapper class to sort choices alphabetically.
    '''


class SortedSelect(SortedSelectMixin, forms.Select):
    '''
    Wrapper class to sort choices alphabetically.
    '''


class ProfileForm(forms.ModelForm):
    '''
    User profile editing.
    '''
    class Meta(object):
        model = Profile
        fields = (
            'language',
            'languages',
            'secondary_languages',
        )
        widgets = {
            'language': SortedSelect,
            'languages': SortedSelectMultiple,
            'secondary_languages': SortedSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # Limit languages to ones which have translation
        qs = Language.objects.have_translation()
        self.fields['languages'].queryset = qs
        self.fields['secondary_languages'].queryset = qs


class SubscriptionForm(forms.ModelForm):
    '''
    User subscription management.
    '''
    class Meta(object):
        model = Profile
        fields = (
            'subscriptions',
            'subscribe_any_translation',
            'subscribe_new_string',
            'subscribe_new_suggestion',
            'subscribe_new_contributor',
            'subscribe_new_comment',
            'subscribe_new_language',
            'subscribe_merge_failure',
        )
        widgets = {
            'subscriptions': forms.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):

        super(SubscriptionForm, self).__init__(*args, **kwargs)
        user = kwargs['instance'].user
        self.fields['subscriptions'].help_text = None
        self.fields['subscriptions'].required = False
        self.fields['subscriptions'].queryset = Project.objects.all_acl(user)


class UserForm(forms.ModelForm):
    '''
    User information form.
    '''
    username = UsernameField()
    email = forms.ChoiceField(
        label=_('E-mail'),
        help_text=_(
            'You can add another emails on Authentication tab.'
        ),
        choices=(
            ('', ''),
        ),
        required=True
    )

    class Meta(object):
        model = User
        fields = (
            'username',
            'first_name',
            'email',
        )

    def __init__(self, *args, **kwargs):

        super(UserForm, self).__init__(*args, **kwargs)

        verified_mails = VerifiedEmail.objects.filter(
            social__user=self.instance
        )
        emails = set([x.email for x in verified_mails])
        emails.add(self.instance.email)

        self.fields['first_name'].required = True
        self.fields['first_name'].label = _('Full name')
        self.fields['email'].choices = [(x, x) for x in emails]
        self.fields['username'].valid = self.instance.username


class ContactForm(forms.Form):
    '''
    Form for contacting site owners.
    '''
    subject = forms.CharField(label=_('Subject'), required=True)
    name = forms.CharField(label=_('Your name'), required=True)
    email = forms.EmailField(label=_('Your email'), required=True)
    message = forms.CharField(
        label=_('Message'),
        required=True,
        widget=forms.Textarea
    )
    content = forms.CharField(required=False)

    def clean_content(self):
        '''
        Check if content is empty.
        '''
        if self.cleaned_data['content'] != '':
            raise forms.ValidationError('Invalid value')
        return ''


class EmailForm(forms.Form):
    '''
    Email change form.
    '''
    required_css_class = "required"
    error_css_class = "error"

    email = NoStripEmailField(
        max_length=75,
        label=_("E-mail"),
        help_text=_('Activation email will be sent here.'),
    )
    content = forms.CharField(required=False)

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(
                _(
                    "This email address is already in use. "
                    "Please supply a different email address."
                )
            )
        return self.cleaned_data['email']

    def clean_content(self):
        '''
        Check if content is empty.
        '''
        if self.cleaned_data['content'] != '':
            raise forms.ValidationError('Invalid value')
        return ''


class RegistrationForm(EmailForm):
    '''
    Registration form.
    '''
    required_css_class = "required"
    error_css_class = "error"

    username = UsernameField()
    first_name = forms.CharField(label=_('Full name'))
    content = forms.CharField(required=False)

    def clean_content(self):
        '''
        Check if content is empty.
        '''
        if self.cleaned_data['content'] != '':
            raise forms.ValidationError('Invalid value')
        return ''


class CaptchaRegistrationForm(RegistrationForm):
    '''
    Registration form with captcha protection.
    '''
    captcha = forms.IntegerField(required=True)
    captcha_id = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, data=None, *args, **kwargs):
        super(CaptchaRegistrationForm, self).__init__(
            data,
            *args,
            **kwargs
        )

        # Load data
        self.tampering = False
        if data is None or 'captcha_id' not in data:
            self.captcha = MathCaptcha()
        else:
            try:
                self.captcha = MathCaptcha.from_hash(data['captcha_id'])
            except ValueError:
                self.captcha = MathCaptcha()
                self.tampering = True

        # Set correct label
        self.fields['captcha'].label = _('What is %s?') % self.captcha.display
        self.fields['captcha_id'].initial = self.captcha.hashed

    def clean_captcha(self):
        '''
        Validation for captcha.
        '''
        if (self.tampering
                or not self.captcha.validate(self.cleaned_data['captcha'])):
            raise forms.ValidationError(
                _('Please check your math and try again.')
            )

        if 'email' in self.cleaned_data:
            mail = self.cleaned_data['email']
        else:
            mail = 'NONE'

        weblate.logger.info(
            'Passed captcha for %s (%s = %s)',
            mail,
            self.captcha.question,
            self.cleaned_data['captcha']
        )


class PasswordForm(forms.Form):
    '''
    Form for setting password.
    '''
    password1 = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        label=_("New password"),
        help_text=_('At least six characters long.'),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        label=_("New password (again)"),
        help_text=_(
            'Repeat the password so we can verify '
            'you typed it in correctly.'
        ),
    )

    def clean_password1(self):
        '''
        Password validation, requires length of six chars.
        '''
        if len(self.cleaned_data['password1']) < 6:
            raise forms.ValidationError(
                _(u'Password needs to have at least six characters.')
            )
        return self.cleaned_data['password1']

    def clean(self):
        """
        Verify that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data.get('password2', '')

        if password1 != password2:
            raise forms.ValidationError(
                _('You must type the same password each time.')
            )

        return self.cleaned_data


class PasswordChangeForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        label=_("Current password"),
    )


class ResetForm(EmailForm):
    def clean_email(self):
        users = User.objects.filter(email__iexact=self.cleaned_data['email'])

        if not users.exists():
            raise forms.ValidationError(
                _('User with this email address was not found.')
            )
        return users[0]


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):

        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].label = _('Username or email')
        self.fields['password'].label = _('Password')


class HostingForm(forms.Form):
    '''
    Form for asking for hosting.
    '''
    name = forms.CharField(label=_('Your name'), required=True)
    email = forms.EmailField(label=_('Your email'), required=True)
    project = forms.CharField(label=_('Project name'), required=True)
    url = forms.URLField(label=_('Project website'), required=True)
    repo = forms.CharField(
        label=_('Git repository'),
        help_text=_(
            'URL of Git repository, use weblate://project/subproject '
            'for sharing with other subproject.'
        ),
        required=True
    )
    mask = forms.CharField(
        label=_('File mask'),
        help_text=_(
            'Path of files to translate, use * instead of language code, '
            'for example: po/*.po or locale/*/LC_MESSAGES/django.po.'
        ),
        required=True
    )

    message = forms.CharField(
        label=_('Additional message'),
        required=True,
        widget=forms.Textarea
    )
    content = forms.CharField(required=False)

    def clean_content(self):
        '''
        Check if content is empty.
        '''
        if self.cleaned_data['content'] != '':
            raise forms.ValidationError('Invalid value')
        return ''
