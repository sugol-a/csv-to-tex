#!/usr/bin/env python3

import csv
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "3.0")
from gi.repository import Gtk, GtkSource

class ApplicationWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="CSV2TeX")

        self.set_size_request(800, 600)

        self.mainbox = Gtk.Box(margin=12, spacing=12, orientation=Gtk.Orientation.VERTICAL)

        self.file_chooser = Gtk.FileChooserButton()
        self.file_chooser.connect("file-set", self.update_content)
        self.mainbox.pack_start(self.file_chooser, True, True, 0)

        self.io_box = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.io_box.set_position(300)
        self.io_box.set_wide_handle(True)

        self.csv_textview = GtkSource.View(monospace=True, editable=False)
        self.csv_frame = Gtk.Frame(label="CSV", shadow_type=Gtk.ShadowType.IN)
        self.csv_frame.set_size_request(300, 500)
        self.csv_frame.add(self.csv_textview)

        self.tex_textview = GtkSource.View(monospace=True, editable=False)
        self.tex_frame = Gtk.Frame(label="TeX", shadow_type=Gtk.ShadowType.IN)
        self.tex_frame.set_size_request(300, 500)
        self.tex_frame.add(self.tex_textview)

        self.io_box.pack1(self.csv_frame)
        self.io_box.pack2(self.tex_frame)

        self.options_box = Gtk.FlowBox()
        self.checkboxes = Gtk.VBox()
        self.chk_header_rule = Gtk.CheckButton(label="Header rule")
        self.chk_header_rule.connect("toggled", self.update_content)
        self.chk_row_rules = Gtk.CheckButton(label="Row rules")
        self.chk_row_rules.connect("toggled", self.update_content)
        self.chk_col_rules = Gtk.CheckButton(label="Column rules")
        self.chk_col_rules.connect("toggled", self.update_content)

        self.checkboxes.pack_start(self.chk_header_rule, True, True, 0)
        self.checkboxes.pack_start(self.chk_row_rules, True, True, 0)
        self.checkboxes.pack_start(self.chk_col_rules, True, True, 0)
        self.options_box.add(self.checkboxes)

        self.alignment_frame = Gtk.Frame(label="Alignment")
        self.alignment_box = Gtk.VBox()
        self.rd_align_left = Gtk.RadioButton(label="Left")
        self.rd_align_left.connect("toggled", self.update_content)
        self.rd_align_center = Gtk.RadioButton.new_with_label_from_widget(self.rd_align_left,
                                                                         "Center")
        self.rd_align_center.connect("toggled", self.update_content)
        self.rd_align_right = Gtk.RadioButton.new_with_label_from_widget(self.rd_align_left,
                                                                         "Right")
        self.rd_align_right.connect("toggled", self.update_content)

        self.alignment_box.add(self.rd_align_left)
        self.alignment_box.add(self.rd_align_center)
        self.alignment_box.add(self.rd_align_right)
        self.alignment_frame.add(self.alignment_box)
        self.options_box.add(self.alignment_frame)

        self.mainbox.pack_start(self.io_box, True, True, 0)
        self.mainbox.pack_start(self.options_box, True, True, 0)
        self.add(self.mainbox)

        lang_manager = GtkSource.LanguageManager.get_default()
        csv_lang = lang_manager.get_language("csv")
        tex_lang = lang_manager.get_language("latex")

        self.csv_textview.get_buffer().set_language(csv_lang)
        self.tex_textview.get_buffer().set_language(tex_lang)

    def update_content(self, widget):
        filename = self.file_chooser.get_filename()
        if not filename:
            return

        # Get the alignment character
        alignment = next((radio for radio in self.rd_align_left.get_group() if radio.get_active() )).get_label().lower()[0]

        header_rule = self.chk_header_rule.get_active()
        row_rule = self.chk_row_rules.get_active()
        col_rule = self.chk_col_rules.get_active()

        with open(filename) as infile:
            reader = csv.reader(infile)
            n_cols = len(next(reader))

            infile.seek(0)

            csv_buffer = self.csv_textview.get_buffer()
            csv_buffer.set_text("".join(infile.readlines()))
            self.csv_textview.set_buffer(csv_buffer)

            tex_buffer = self.tex_textview.get_buffer()

            alignment_string = None
            if col_rule:
                alignment_string = f"""{'|'.join([alignment for i in range(n_cols)])}"""
            else:
                alignment_string = f"""{alignment * n_cols}"""

            tex_buffer.set_text(f"""\\begin{{tabular}}{{{alignment_string}}}\n""")

            infile.seek(0)
            first_row = True
            for row in reader:
                tex_line = "    " + " & ".join(row) + " \\\\"

                if row_rule or (header_rule and first_row):
                    tex_line += " \\hline \\\\"

                tex_line += "\n"
                tex_buffer.insert(tex_buffer.get_end_iter(), tex_line)

                first_row = False

            tex_buffer.insert(tex_buffer.get_end_iter(), "\end{tabular}")

def main():
    # with open(sys.argv[1]) as infile:
    #     csvfile = csv.reader(infile)

    #     for row in csvfile:
    #         print(" & ".join(row) + "\\\\")

    win = ApplicationWindow()
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
