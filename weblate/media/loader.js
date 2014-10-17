jQuery.fn.extend({
    insertAtCaret: function (myValue) {
        return this.each(function (i) {
            if (document.selection) {
                // For browsers like Internet Explorer
                this.focus();
                sel = document.selection.createRange();
                sel.text = myValue;
                this.focus();
            } else if (this.selectionStart || this.selectionStart == '0') {
                //For browsers like Firefox and Webkit based
                var startPos = this.selectionStart;
                var endPos = this.selectionEnd;
                var scrollTop = this.scrollTop;
                this.value = this.value.substring(0, startPos) + myValue + this.value.substring(endPos, this.value.length);
                this.focus();
                this.selectionStart = startPos + myValue.length;
                this.selectionEnd = startPos + myValue.length;
                this.scrollTop = scrollTop;
            } else {
                this.value += myValue;
                this.focus();
            }
        });
    }
});


function text_change(e) {
    if (e.key && e.key == 'Tab') {
        return;
    }
    $(this).parents('form').find('[name=fuzzy]').prop('checked', false);
}

function mt_set(txt) {
    $('#id_target').val(txt).change();
    $('#id_fuzzy').prop('checked', true);
}

var loading = 0;
var mt_loaded = false;

function inc_loading() {
    if (loading === 0) {
        $('#mt-loading').show();
    }
    loading++;
}

function dec_loading() {
    loading--;
    if (loading === 0) {
        $('#mt-loading').hide();
    }
}

function get_source_string(callback) {
    $('#loading').show();
    $.get($('#js-get').attr('href'), function (data) {
        callback(data);
        $('#loading').hide();
    });
}

function process_machine_translation(data, textStatus, jqXHR) {
    dec_loading();
    if (data.responseStatus == 200) {
        var lang = $('.translation_html_markup').attr('lang');
        var dir = $('.translation_html_markup').attr('dir');
        data.translations.forEach(function (el, idx, ar) {
            var new_row = $('<tr/>').data('quality', el.quality);
            var done = false;
            new_row.append($('<td/>').attr('class', 'translatetext target').attr('lang', lang).attr('dir', dir).text(el.text));
            new_row.append($('<td/>').attr('class', 'translatetext').text(el.source));
            new_row.append($('<td/>').text(el.service));
            /* Translators: Verb for copy operation */
            new_row.append($('<td><a class="copymt small-button">' + gettext('Copy') + '</a></td>'));
            $('#machine-translations').children('tr').each(function (idx) {
                if ($(this).data('quality') < el.quality && !done) {
                    $(this).before(new_row);
                    done = true;
                }
            });
            if (! done) {
                $('#machine-translations').append(new_row);
            }
        });
        $('a.copymt').button({text: true, icons: { primary: "ui-icon-copy" }}).click(function () {
            var text = $(this).parent().parent().find('.target').text();
            mt_set(text);
        });
    } else {
        var msg = interpolate(
            gettext('The request for machine translation using %s has failed:'),
            [data.service]
        );
        $('#mt-errors').append(
            $('<li>' + msg + ' ' + data.responseDetails + '</li>')
        );
    }
}

function failed_machine_translation(jqXHR, textStatus, errorThrown) {
    dec_loading();
    $('#mt-errors').append(
        $('<li>' + gettext('The request for machine translation has failed:') + ' ' + textStatus + '</li>')
    );
}

function load_machine_translations() {
    if (mt_loaded) {
        return;
    }
    mt_loaded = true;
    MACHINE_TRANSLATION_SERVICES.forEach(function (el, idx, ar) {
        inc_loading();
        $.ajax({
            url: $('#js-translate').attr('href') + '?service=' + el,
            success: process_machine_translation,
            error: failed_machine_translation,
            dataType: 'json'
        });
    });
}

function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function cell_cmp(a, b) {
    if (a.indexOf('%') != -1 && b.indexOf('%') != -1) {
        a = parseFloat(a.replace(',', '.'));
        b = parseFloat(b.replace(',', '.'));
    } else if (isNumber(a) && isNumber(b)) {
        a  = parseFloat(a);
        b  = parseFloat(b);
    } else {
        a = a.toLowerCase();
        b = b.toLowerCase();
    }
    if (a == b) {
        return 0;
    }
    if (a > b) {
        return 1;
    }
    return -1;
}

function load_table_sorting() {
    $('table.sort').each(function () {
        var table = $(this),
            tbody = table.find('tbody'),
            thead = table.find('thead'),
            thIndex = 0;
        $(this).find('thead th')
            .each(function () {

            var th = $(this),
                inverse = 1;
            // handle colspan
            if (th.attr('colspan')) {
                thIndex += parseInt(th.attr('colspan'), 10) - 1;
            }
            // skip empty cells and cells with icon (probably already processed)
            if (th.text() !== '' && th.find('span.ui-icon').length === 0) {
                // Store index copy
                var myIndex = thIndex;
                // Add icon, title and class
                th.attr('title', gettext("Sort this column")).addClass('sort').append('<span class="sort ui-icon ui-icon-carat-2-n-s" />');

                // Click handler
                th.click(function () {

                    tbody.find('td,th').filter(function () {
                        return $(this).index() === myIndex;
                    }).sortElements(function (a, b) {
                        return inverse * cell_cmp($.text([a]), $.text([b]));
                    }, function () {

                        // parentNode is the element we want to move
                        return this.parentNode;

                    });
                    thead.find('span.sort').removeClass('ui-icon-carat-1-n ui-icon-carat-1-s').addClass('ui-icon-carat-2-n-s');
                    if (inverse == 1) {
                        $(this).find('span.sort').addClass('ui-icon-carat-1-n').removeClass('ui-icon-carat-2-n-s');
                    } else {
                        $(this).find('span.sort').addClass('ui-icon-carat-1-s').removeClass('ui-icon-carat-2-n-s');
                    }

                    inverse = inverse * -1;

                });
            }
            // Increase index
            thIndex += 1;
        });

    });
}

function zen_editor(e) {
    var $this = $(this);
    var $row = $this.parents('tr');
    var checksum = $row.find('[name=checksum]').val();

    $row.addClass('translation-modified');

    var form = $row.find('form');
    $('#loading-' + checksum).show();
    $('#messages-' + checksum).html('');
    $.post(
        form.attr('action'),
        form.serialize(),
        function (data) {
            $('#loading-' + checksum).hide();
            $('#messages-' + checksum).append(data);
            $row.removeClass('translation-modified').addClass('translation-saved');
        }
    );
}

function init_editor(editors) {
    editors.autogrow();
}

$(function () {
    $('.button').button();
    $('#breadcrumbs').buttonset();
    $('.sug-accept').button({text: false, icons: { primary: "ui-icon-check" }});
    $('.sug-delete').button({text: false, icons: { primary: "ui-icon-close" }});
    $('.sug-upvote').button({text: false, icons: { primary: "ui-icon-plusthick" }});
    $('.sug-downvote').button({text: false, icons: { primary: "ui-icon-minusthick" }});
    $('.historybutton').button({text: true, icons: { primary: "ui-icon-arrowreturn-1-w" }});
    $('.edit-priority').button({text: false, icons: { primary: "ui-icon-pencil" }}).click(function (e) {
        var form = $('#priority_form');
        form.find('form').attr('action', $(this).attr('href'));
        form.find('#id_priority').val($(this).data('priority'));
        form.dialog({
            modal: true,
            autoOpen: true,
            buttons: [
                {
                    text: gettext("Ok"),
                    click: function () {
                        $(this).find('form').submit();
                        $(this).dialog("close");
                    }
                },
                {
                    text: gettext("Cancel"),
                    click: function () {
                        $(this).dialog("close");
                    }
                }
            ]
        });
        e.preventDefault();
    });
    $('#navi').buttonset();
    $('#button-first').button({text: false, icons: { primary: "ui-icon-seek-first" }});
    $('#button-next').button({text: false, icons: { primary: "ui-icon-seek-next" }});
    $('#button-pos').button({text: true});
    $('#button-prev').button({text: false, icons: { primary: "ui-icon-seek-prev" }});
    $('#button-end').button({text: false, icons: { primary: "ui-icon-seek-end" }});
    $('#navi .button-disabled').button('disable');
    var translation_editor = $('.translation-editor');
    if (translation_editor.length > 0) {
        $(document).on('change', '.translation-editor', text_change);
        $(document).on('keypress', '.translation-editor', text_change);
        init_editor(translation_editor);
        translation_editor.get(0).focus();
        if ($('#button-first').length > 0) {
            Mousetrap.bindGlobal('alt+end', function(e) {window.location = $('#button-end').attr('href'); return false;});
            Mousetrap.bindGlobal('alt+pagedown', function(e) {window.location = $('#button-next').attr('href'); return false;});
            Mousetrap.bindGlobal('alt+pageup', function(e) {window.location = $('#button-prev').attr('href'); return false;});
            Mousetrap.bindGlobal('alt+home', function(e) {window.location = $('#button-first').attr('href'); return false;});
            Mousetrap.bindGlobal('alt+enter', function(e) {$('.translation-form').submit(); return false;});
            Mousetrap.bindGlobal('ctrl+enter', function(e) {$('.translation-form').submit(); return false;});
        }
    }
    $('#toggle-direction').buttonset().change(function (e) {
        $('.translation-editor').attr('dir', $("#toggle-direction :radio:checked").attr('value')).focus();
    });
    $('#copy-text').button({text: true, icons: { primary: "ui-icon-arrow-1-s" }}).click(function f() {
        get_source_string(function (data) {
            mt_set(data);
        });
        return false;
    });
    $('.specialchar').button().click(function () {
        var text = $(this).text();
        if (text == '\\t') {
            text = '\t';
        } else if (text == '→') {
            text = '\t';
        } else if (text == '↵') {
            text = '\r';
        }
        $('#id_target').insertAtCaret(text);
    });
    $('.ignorecheck').button({text: false, icons: { primary: "ui-icon-close" }}).click(function () {
        var parent_id = $(this).parent()[0].id;
        var check_id = parent_id.substring(6);
        $.get($(this).attr('href'), function () {
            $('#' + parent_id).remove();
        });
        return false;
    });
    load_table_sorting();
    $("#translate-tabs").tabs({
        ajaxOptions: {
            error: function (xhr, status, index, anchor) {
                $(anchor.hash).html(gettext("AJAX request to load this content has failed!"));
            }
        },
        cache: true,
        beforeLoad: function (e, ui) {
            var $panel = $(ui.panel);

            if ($panel.is(":empty")) {
                $panel.append("<div class='tab-loading'>" + gettext("Loading…") + "</div>");
            }
            ui.jqXHR.error(function () {
                $panel.find('.tab-loading').html(gettext("AJAX request to load this content has failed!"));
            });
        },
        load: function (e, ui) {
            $(ui.panel).find(".tab-loading").remove();
            $('a.mergebutton').button({text: true, icons: { primary: "ui-icon-check" }});
            $('.button').button();
            $('a.copydict').button({text: true, icons: { primary: "ui-icon-copy" }}).click(function () {
                var text = $(this).parent().parent().find('.target').text();
                $('#id_target').insertAtCaret(text);
            });
        },
        create: function (e, ui) {
            /* Machine translations loading */
            if (ui.panel.attr('id') == 'tab-machine') {
                load_machine_translations();
            }
        },
        activate: function (e, ui) {
            /* Machine translations loading */
            if (ui.newPanel.attr('id') == 'tab-machine') {
                load_machine_translations();
            }
            $.cookie('translate-tab', ui.newTab.index(), {path: '/', expires: 31});
        },
        active: $.cookie('translate-tab')
    });
    $("div.tabs").tabs({
        ajaxOptions: {
            error: function (xhr, status, index, anchor) {
                $(anchor.hash).html(gettext("AJAX request to load this content has failed!"));
            }
        },
        cache: true,
        load: function (e, ui) {
            $(ui.panel).find(".tab-loading").remove();
            load_table_sorting();
            $('.buttons').buttonset();
            $('.buttons .disabled').button('disable');
            $('.details-accordion').accordion({collapsible: true, active: false});
            $('.confirm-reset').click(function () {

                $('<div title="' + gettext('Confirm resetting repository') + '"><p>' + gettext('Resetting the repository will throw away all local changes!') + '</p></div>').dialog({
                    modal: true,
                    autoOpen: true,
                    buttons: [
                        {
                            text: gettext("Ok"),
                            click: function () {
                                window.location = $('.confirm-reset').attr('href');
                                $(this).dialog("close");
                            }
                        },
                        {
                            text: gettext("Cancel"),
                            click: function () {
                                $(this).dialog("close");
                            }
                        }
                    ]
                });
                return false;
            });
        },
        beforeLoad: function (e, ui) {
            var $panel = $(ui.panel);

            if ($panel.is(":empty")) {
                $panel.append("<div class='tab-loading'>" + gettext("Loading…") + "</div>");
            }
            ui.jqXHR.error(function () {
                $panel.find('.tab-loading').html(gettext("AJAX request to load this content has failed!"));
            });

        }
    });
    $("#id_date").datepicker({ dateFormat: "yy-mm-dd" });
    $("form.autosubmit select").change(function () {
        $("form.autosubmit").submit();
    });
    $('#s_content').hide();
    $('#id_content').parent('td').parent('tr').hide();
    $('.expander').click(function () {
        var $table_row = $(this).parent();
        var $next_row = $table_row.next();
        $table_row.find('.expander-icon').toggleClass('ui-icon-triangle-1-s').toggleClass('ui-icon-triangle-1-e');
        $next_row.toggle();
        var $loader = $next_row.find('tr.details .load-details');
        if ($loader.length > 0) {
            var url = $loader.attr('href');
            $loader.remove();
            $.get(
                url,
                function (data) {
                    var $cell = $next_row.find('tr.details td');
                    $cell.find('img').remove();
                    $cell.append(data);
                    $cell.find('.button').button();
                }
            );
        }
    });
    $('.code-example').focus(function () {
        $(this).select();
    });
    $('a.disconnect').click(function (e) {
        e.preventDefault();
        $('form#disconnect-form')
            .attr('action', $(this).attr('href'))
            .submit();
    });

    $(document).tooltip({
        content: function () {
            var element = $(this);
            var content = $(this).find('.tooltip-content');
            if (content.length > 0) {
                element = content;
            }
            return element.html();
        },
        items: ".tooltip"
    });
    if (update_lock) {
        window.setInterval(function () {
            $.get($('#js-lock').attr('href'));
        }, 19000);
    }
    if ($('.zen').length > 0) {
        $(window).scroll(function(){
            if ($(window).scrollTop() >= $(document).height() - (2 * $(window).height())) {
                if ($('#last-section').length > 0 || $('#loading-next').css('display') != 'none') {
                    return;
                }
                $('#loading-next').show();

                var loader = $('#zen-load');
                loader.data('offset', 20 + parseInt(loader.data('offset')));

                $.get(
                    loader.attr('href') + '&offset=' + loader.data('offset'),
                    function (data) {
                        $('#loading-next').hide();

                        $('.zen tbody').append(data).find('.button').button();

                        var $editors = $('.translation-editor');

                        init_editor($editors);
                    }
                );
            }
        });
        $(document).on('change', '.translation-editor', zen_editor);
        $(document).on('change', '.fuzzy_checkbox', zen_editor);

        $(window).on('beforeunload', function(){
            if ($('.translation-modified').length > 0) {
                return gettext('There are some unsaved changes, are you sure you want to leave?');
            }
        });

    }
});
