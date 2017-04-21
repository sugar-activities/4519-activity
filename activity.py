#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#   activity.py by/por:
#   Agustin Zubiaga <aguzubiaga97@gmail.com>
#   Daniel Francis <santiago.danielfrancis@gmail.com>
#   Sugarlabs - CeibalJAM! - Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys

import gettext
LOCALE_DIR = os.path.join(".", "locale")
TRANSLATION_DOMAIN = "jamedit"
gettext.install(TRANSLATION_DOMAIN, LOCALE_DIR)

import pango
import gtk

import sugar
from sugar import mime
from sugar.graphics import iconentry
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toggletoolbutton import ToggleToolButton
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.activity.widgets import EditToolbar, StopButton, \
                                   ActivityToolbarButton, ToolbarButton
from sugar.datastore import datastore
from sugar.activity import activity

from font_options import FontToolbarButton
from editor import Editor, LANGUAGE_MANAGER, LANGUAGES
import file_choosers
file_choosers.langsmanager = LANGUAGE_MANAGER
file_choosers.langs = LANGUAGES


class JAMEdit(activity.Activity):

        def __init__(self, handle):
                activity.Activity.__init__(self, handle, True)

                self.max_participants = 1

                # ****** Editor ******

                self.editor = Editor(self)
                self.editor.set_size_request(800, 790)
                scroll = gtk.ScrolledWindow()
                scroll.set_policy(gtk.POLICY_AUTOMATIC,
                                  gtk.POLICY_AUTOMATIC)
                scroll.add(self.editor)
                scroll.show_all()

                vbox = gtk.VBox()
                vbox.pack_start(scroll, True, True, 0)
                vbox.show_all()

                self.set_canvas(vbox)

                # ****** Toolbars ******

                self.toolbar_box = ToolbarBox()

                activity_button = ActivityToolbarButton(self)
                activity_toolbar = activity_button.page

                # Abrir objeto / Open object
                open_obj_btn = ToolButton("open-from-journal")
                open_obj_btn.connect("clicked",
                                   file_choosers.open_from_journal, None, self)
                open_obj_btn.set_tooltip(_("Open object from journal"))
                activity_toolbar.insert(open_obj_btn, -1)

                # Separador / Separator
                separator = gtk.SeparatorToolItem()
                separator.set_draw(True)
                separator.set_expand(False)
                activity_toolbar.insert(separator, -1)

                # ****** Open File button ******
                open_btn = ToolButton("fileopen")
                open_btn.set_tooltip(_("Open File"))
                open_btn.set_accelerator('<ctrl>o')
                open_btn.connect("clicked", self.open_file)
                activity_toolbar.insert(open_btn, -1)

                # ****** Save File button ******
                save_btn = ToolButton("stock_save")
                save_btn.set_tooltip(_("Save this file"))
                save_btn.set_accelerator('<ctrl>s')
                save_btn.connect("clicked", self.save_file)
                activity_toolbar.insert(save_btn, -1)

                activity_toolbar.show_all()
                activity_toolbar.stop.hide()

                # Guardar como / Save As
                save_as = gtk.MenuItem(_("Save on the file system."))
                activity_toolbar.keep.props.palette.menu.append(save_as)
                save_as.connect("activate", self.save_file_as)
                save_as.show()

                # Nuevo / New
                new = ToolButton("new")
                new.set_tooltip(_("New file"))
                new.set_accelerator('<ctrl>n')
                new.connect("clicked", self.new)
                activity_toolbar.insert(new, 6)
                new.show()

                activity_toolbar.keep.show()

                self.toolbar_box.toolbar.insert(activity_button, 0)

                # Edicion / Edit Toolbar

                edit_toolbar = EditToolbar()
                edit_toolbar_button = ToolbarButton(label=_("Edit"),
                                                    page=edit_toolbar,
                                                    icon_name='toolbar-edit')

                edit_toolbar.cut = ToolButton("cut")
                edit_toolbar.cut.set_tooltip(_("Cut"))
                edit_toolbar.cut.set_accelerator('<ctrl>x')
                edit_toolbar.insert(edit_toolbar.cut, 4)

                separator = gtk.SeparatorToolItem()
                separator.set_draw(False)
                separator.set_expand(True)
                edit_toolbar.insert(separator, -1)

                edit_toolbar.pep8_btn = ToolButton('pep8')
                edit_toolbar.pep8_btn.set_tooltip(_("PEP 8 Check"))
                edit_toolbar.pep8_btn.connect("clicked", self.pep8_check)
                edit_toolbar.insert(edit_toolbar.pep8_btn, -1)

                edit_toolbar.pep8_datetime_separator = gtk.SeparatorToolItem()
                edit_toolbar.pep8_datetime_separator.set_draw(True)
                edit_toolbar.insert(edit_toolbar.pep8_datetime_separator, -1)

                insert_datetime = ToolButton("insert-datetime")
                insert_datetime.connect("clicked",
                                        self.editor._insert_date_time)
                insert_datetime.set_tooltip(_("Insert date and time"))
                edit_toolbar.insert(insert_datetime, -1)
                insert_datetime.show_all()

                edit_toolbar.copy.connect("clicked", self.editor._copy_cb)
                edit_toolbar.paste.connect("clicked", self.editor._paste_cb)
                edit_toolbar.undo.connect("clicked", self.editor._undo_cb)
                edit_toolbar.redo.connect("clicked", self.editor._redo_cb)
                edit_toolbar.cut.connect("clicked", self.editor._cut_cb)

                edit_toolbar.show_all()
                edit_toolbar.pep8_btn.hide()
                edit_toolbar.pep8_datetime_separator.set_draw(False)

                self.toolbar_box.toolbar.insert(edit_toolbar_button, -1)

                self.edit_toolbar = edit_toolbar

                # Separador / Separator
                separator = gtk.SeparatorToolItem()
                separator.set_draw(False)
                self.toolbar_box.toolbar.insert(separator, -1)

                # Buscar / Search
                search_entry = iconentry.IconEntry()
                search_entry.set_size_request(gtk.gdk.screen_width() / 3, -1)
                search_entry.set_icon_from_name(
                        iconentry.ICON_ENTRY_PRIMARY, 'system-search')
                search_entry.add_clear_button()
                search_entry.connect('activate',
                                     self.editor._search_entry_activate_cb)
                search_entry.connect('changed',
                                     self.editor._search_entry_changed_cb)
                search_item = gtk.ToolItem()
                search_item.add(search_entry)
                self.toolbox.toolbar.insert(search_item, -1)

                self._search_prev = ToolButton('go-previous-paired')
                self._search_prev.set_tooltip(_('Previous'))
                self._search_prev.connect('clicked',
                                          self.editor._search_prev_cb)
                self.toolbox.toolbar.insert(self._search_prev, -1)

                self._search_next = ToolButton('go-next-paired')
                self._search_next.set_tooltip(_('Next'))
                self._search_next.connect('clicked',
                                          self.editor._search_next_cb)
                self.toolbox.toolbar.insert(self._search_next, -1)

                # Preferencias / preferences

                preferences_toolbar = gtk.Toolbar()

                show_line_numbers = ToggleToolButton('show-numbers')
                show_line_numbers.set_tooltip(_("Show line numbers"))

                show_line_numbers.set_active(True)
                show_line_numbers.connect("clicked", \
                                     self.editor._set_show_line_numbers)
                show_line_numbers.show()
                preferences_toolbar.insert(show_line_numbers, -1)

                self.editor._make_languages_combo(preferences_toolbar)
                self.editor.make_style_combo(preferences_toolbar)

                preferences = ToolbarButton()
                preferences.props.page = preferences_toolbar
                preferences.props.icon_name = 'preferences-system'
                preferences.show_all()

                self.toolbar_box.toolbar.insert(preferences, -1)

                font_options = FontToolbarButton()
                font_options.connect("load-pango-context",
                                     self.load_pango_context)
                font_options.load_toolbar()
                font_options.connect("font-changed", self.change_font)
                self.toolbar_box.toolbar.insert(font_options, -1)
                font_options.show()

                # Separador / Separator

                separator = gtk.SeparatorToolItem()
                separator.set_draw(False)
                separator.set_expand(True)
                self.toolbar_box.toolbar.insert(separator, -1)

                # Boton salir / Stop Button

                exit = StopButton(self)
                self.toolbar_box.toolbar.insert(exit, -1)

                self.toolbar_box.show_all()

                self.set_toolbar_box(self.toolbar_box)

                # Barra de estado de PEP8 / PEP8 status bar
                self.pep8_bar = gtk.Statusbar()
                self.pep8_bar.label = gtk.Label()
                self.pep8_bar.add(self.pep8_bar.label)
                vbox.pack_end(self.pep8_bar, False, True, 0)

        def change_font(self, widget, family, face, size):
                self.editor.modify_font(
               pango.FontDescription("%s %s %d" % (family, face, size)))

        def load_pango_context(self, widget):
                return self.editor.get_pango_context()

        def pep8_check(self, widget):
                self.editor.pep8.check_file(self.editor._get_all_text(),
                                            self.editor)

        def close(self, skip_save=False):
                close = True
                if not self.editor.file:
                        close = self.save_file(None, type="exit", mode=2)
                if close:
                        activity.Activity.close(self)

        def open_file(self, widget, from_journal=False):
                self.editor.pep8.check_exit()
                self.save_file(None, type="exit")
                if not from_journal:
                        file_path, remember = file_choosers.open_file_dialog()
                        if file_path != None:
                                self.set_title(os.path.split(file_path)[-1])
                                mime_type = mime.get_from_file_name(file_path)
                                self.metadata["mime_type"] = mime_type

                                file = open(file_path, "r")
                                self.editor.buffer.set_text(file.read())
                                if remember:
                                        self.editor.file = file_path
                                self.editor._search_and_active_language(
                                                                     mime_type)
                                file.close()

                if from_journal:
                        file_path = from_journal
                        mime_type = mime.get_from_file_name(file_path)
                        self.metadata["mime_type"] = mime_type

                        file = open(file_path, "r")
                        self.editor.buffer.set_text(file.read())
                        self.editor.file = file_path
                        self.editor._search_and_active_language(mime_type)
                        file.close()

        def new(self, widget):
                self.editor.pep8.check_exit()
                _continue = self.save_file(None, type="exit")
                if _continue:
                        self.metadata["mime_type"] = mime.GENERIC_TYPE_TEXT
                        self.editor.lang = None
                        self.editor.file = None
                        self.editor.lang_combo.set_active(0)
                        self.editor.buffer.set_highlight_syntax(False)
                        self.edit_toolbar.pep8_btn.hide()
                        self.edit_toolbar.pep8_datetime_separator.set_draw(
                                                                         False)
                        self.editor.buffer.set_text("")
                        self.set_title(_("New"))

        def save_file_as(self, widget):
                file_path = file_choosers.save_file_dialog()
                if file_path:
                        self.editor.file = file_path
                        file = open(self.editor.file, "w")
                        file.write(self.editor._get_all_text())
                        file.close()

                        self.set_title(os.path.split(file_path)[-1])
                        mime_type = mime.get_from_file_name(file_path)
                        self.metadata["mime_type"] = mime_type
                        self.editor.file = file_path
                        self.editor._search_and_active_language(mime_type)

        def save_file(self, widget, type=None, mode=1):
                if not type:
                        if self.editor.file:
                                file = open(self.editor.file, "w")
                                file.write(self.editor._get_all_text())
                                file.close()
                        else:
                                file_path = file_choosers.save_file_dialog()
                                if file_path:
                                        self.editor.file = file_path
                                        file = open(self.editor.file, "w")
                                        file.write(self.editor._get_all_text())
                                        file.close()
                if type == "exit":
                        dialog = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION)
                        dialog.add_buttons(gtk.STOCK_CANCEL,
                                           gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_NO,
                                           gtk.RESPONSE_NO,
                                           gtk.STOCK_YES,
                                           gtk.RESPONSE_YES)

                        dialog.set_markup("<b>%s</b>" % _("Save changes..."))
                        if mode == 1:
                                dialog.format_secondary_text(
                                            _("Do you want to save changes?"))
                        elif mode == 2:
                                dialog.format_secondary_text(
                        _("Do you want to save changes\nin the file system?"))
                        response = dialog.run()
                        dialog.destroy()
                        if not response == gtk.RESPONSE_CANCEL:
                                if response == gtk.RESPONSE_YES:
                                        if self.editor.file:
                                                file = open(
                                                         self.editor.file, "w")
                                                file.write(
                                                   self.editor._get_all_text())
                                                file.close()
                                        else:
                                                file_path = \
                                        file_choosers.save_file_dialog()
                                                if file_path:
                                                        self.editor.file = \
                                                                      file_path
                                                        file = open(
                                                         self.editor.file, "w")
                                                        file.write(
                                                   self.editor._get_all_text())
                                                        file.close()
                                return True
                        else:
                                return False

        def write_file(self, file_path):
                if self.editor.lang:
                        lang_mime_type = self.editor.lang.get_mime_types()[0]

                elif not self.editor.lang:
                        lang_mime_type = mime.GENERIC_TYPE_TEXT

                self.metadata['mime_type'] = lang_mime_type

                jfile = open(file_path, "w")
                jfile.write(self.editor._get_all_text())
                jfile.close()

        def read_file(self, file_path):
                fpath = open(file_path, "r")
                text = fpath.read()
                fpath.close()

                mime_type = self.metadata["mime_type"]

                self.editor.buffer.set_text(text)
                self.editor._search_and_active_language(mime_type)
