#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#   font_options.py by/por:
#   Daniel Francis <santiago.danielfrancis@gmail.com>
#   Agustin Zubiaga <aguzubiaga97@gmail.com>
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

import gobject
import gtk

from sugar.graphics.combobox import ComboBox
from sugar.graphics.toolcombobox import ToolComboBox
from sugar.activity.widgets import ToolbarButton


class FontToolbarButton(ToolbarButton):
        __gsignals__ = {'load-pango-context': (gobject.SIGNAL_RUN_LAST,
                                                gobject.TYPE_PYOBJECT,
                                                tuple()),
                        'font-changed': (gobject.SIGNAL_RUN_LAST,
                                          gobject.TYPE_NONE,
                                         (gobject.TYPE_STRING,
                                          gobject.TYPE_STRING,
                                          gobject.TYPE_INT))}

        def __init__(self):
                ToolbarButton.__init__(self)
                self.toolbar = gtk.Toolbar()
                self.props.page = self.toolbar
                self.props.icon_name = 'format-text'
                self.family = "Monospace"
                self.current_face = "Regular"

        def size_changed(self, adjustment):
                self.emit("font-changed", self.family,
                          self.current_face, adjustment.get_value())

        def face_changed(self, widget):
                iter = widget.get_active_iter()
                self.current_face = self.faces[self.family].get_value(iter, 0)
                self.emit('font-changed', self.family,
                          self.current_face, self.size_adj.get_value())

        def family_changed(self, widget):
                iter = widget.get_active_iter()
                self.family = self.family_model.get_value(iter, 0)
                self.face_combo.set_model(self.faces[self.family])
                self.face_combo.set_active(0)

        def load_toolbar(self):
                self.context = self.emit("load-pango-context")
                self.family_combo = ComboBox()
                family_renderer = gtk.CellRendererText()
                family_renderer.set_property("family-set", True)
                self.family_combo.pack_start(family_renderer)
                self.family_combo.add_attribute(family_renderer, 'text', 0)
                self.family_combo.add_attribute(family_renderer, 'family', 0)
                self.family_model = gtk.ListStore(str)
                monospace_index = 0
                count = 0
                self.faces = {}
                for i in self.context.list_families():
                        name = i.get_name()
                        monospace_index = count if name == "Monospace" else 0
                        count += 1
                        self.family_model.append([name])
                        family_faces = gtk.ListStore(str, str)
                        for face in i.list_faces():
                                face_name = face.get_face_name()
                                family_faces.append([face_name,
                                                     "%s %s" %
                                                     (name, face_name)])
                        self.faces[name] = family_faces
                self.family_combo.set_model(self.family_model)
                self.family_combo.set_active(monospace_index)
                self.family_combo.connect("changed", self.family_changed)
                self.family_combo.show()
                self.family_tool_item = ToolComboBox(self.family_combo)
                self.family_tool_item.show()
                self.toolbar.insert(self.family_tool_item, -1)

                self.face_combo = ComboBox()
                face_renderer = gtk.CellRendererText()
                face_renderer.set_property("family-set", True)
                self.face_combo.pack_start(face_renderer)
                self.face_combo.add_attribute(face_renderer, 'text', 0)
                self.face_combo.add_attribute(face_renderer, 'font', 1)
                current_model = self.faces["Monospace"]
                self.face_combo.set_model(current_model)
                self.face_combo.set_active(0)
                self.face_combo.connect("changed", self.face_changed)
                self.face_combo.show()
                self.face_tool_item = ToolComboBox(self.face_combo)
                self.face_tool_item.show()
                self.toolbar.insert(self.face_tool_item, -1)

                self.size_adj = gtk.Adjustment(value=10, lower=5,
                                               upper=100, step_incr=1)
                self.size_adj.connect("value-changed", self.size_changed)
                self.size_spin = gtk.SpinButton(self.size_adj)
                self.size_spin.show()
                self.size_spin_item = gtk.ToolItem()
                self.size_spin_item.add(self.size_spin)
                self.size_spin_item.show()
                self.toolbar.insert(self.size_spin_item, -1)

                self.toolbar.show()
