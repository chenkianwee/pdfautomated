"""
Tool for merg size
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from pypdf import PdfReader, PdfWriter

class PdfAutomated(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        # merge tab parameters
        self.nmerge = 0
        self.merge_txt_dict = {}
        self.merge_row_id = 'merge_row_'
        self.merge_txt_id = 'merge_text_'
        self.merge_btn_id = 'merge_btn_'
        self.merge_rmbtn_id = 'merge_rmbtn_'
        # create a box to contain all the parameters
        self.grid_marginx = 1
        self.grid_marginy = 5  
        style_pack_header = Pack(text_align='center', font_weight='bold', font_size=10, background_color='rgba(125, 125, 125, 0.2)', 
                                 color='black')
        
        # Merge tab
        # at least two files for merging
        self.merge_scroller_box = toga.Box(direction=COLUMN)
        nmerge_init = 2
        for _ in range(nmerge_init):
            file_selector = self.add_a_merge_row()
            self.merge_scroller_box.add(file_selector)
            self.nmerge+=1
        
        btn_box = toga.Box(flex=0, direction=COLUMN, margin=(self.grid_marginy, self.grid_marginx))
        add_merge_button = toga.Button("+", on_press=self.add_a_merge_row_user, margin=(self.grid_marginy, self.grid_marginx))
        exe_merge_button = toga.Button("Execute", on_press=self.exe_merge, margin=(self.grid_marginy, self.grid_marginx))
        btn_box.add(add_merge_button)
        btn_box.add(exe_merge_button)
        
        # structure the GUI
        self.merge_scroller = toga.ScrollContainer(
            horizontal=True,
            vertical=True,
            # on_scroll=self.on_scroll,
            flex=1,
            margin=10,
            # background_color="pink",
            )

        self.merge_scroller.content = self.merge_scroller_box
        self.merge_tab = toga.Box(direction=COLUMN)
        self.merge_tab.add(self.merge_scroller)
        self.merge_tab.add(btn_box)
        # Extract tab
        split_tab = toga.Box()
        # Reduce tab
        reduce_tab = toga.Box()
        # tab container
        tabs_container = toga.OptionContainer(flex=1,
                                              style=Pack(margin=(10, 10), align_items='center'),
                                              content=[toga.OptionItem("MergePDF", self.merge_tab),
                                                       toga.OptionItem("ExtractPDF", split_tab),
                                                       toga.OptionItem("ReducePDF", reduce_tab)])
        # main box
        main_box = toga.Box(style=Pack(align_items='center'))
        main_box.add(tabs_container)
        # main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    
    def add_a_merge_row(self):
        row_box = toga.Box(flex=0, id = f"{self.merge_row_id}{self.nmerge}", direction=ROW, margin=(self.grid_marginy, self.grid_marginx))
        path_val_id = f"{self.merge_txt_id}{self.nmerge}"
        select_button = toga.Button("Select", id = f"{self.merge_btn_id}{self.nmerge}", on_press=self.merge_select_file, margin=(self.grid_marginy, self.grid_marginx))
        
        path_val = toga.TextInput(flex=1, id = path_val_id, readonly=True, margin=(self.grid_marginy, self.grid_marginx))
        path_val.enabled = False
        self.merge_txt_dict[path_val_id] = path_val

        row_box.add(path_val)
        row_box.add(select_button)
        return row_box

    def add_a_merge_row_user(self, button):
        row_box = self.add_a_merge_row()
        rm_button = toga.Button("Remove", id = f"{self.merge_rmbtn_id}{self.nmerge}", on_press=self.rm_merge_row_user, margin=(self.grid_marginy, self.grid_marginx))
        row_box.add(rm_button)
        print(self.merge_scroller_box.children)
        nchildren = len(self.merge_scroller_box.children)
        self.merge_scroller_box.insert(nchildren, row_box)
        self.nmerge+=1

    async def merge_select_file(self, button):
        btn_split = button.id.split('_')
        btn_cnt = btn_split[2]
        path_name = await self.main_window.dialog(
            toga.OpenFileDialog(title='Select PDF for Processing'))
        self.merge_txt_dict[f"{self.merge_txt_name}{btn_cnt}"].value = path_name    
    
    def rm_merge_row_user(self, button):
        btn_split = button.id.split('_')
        btn_cnt = btn_split[2]
        merge_children = self.merge_scroller_box.children
        for child in merge_children:
            row_id = child.id
            if row_id == f"{self.merge_row_id}{btn_cnt}":
                self.merge_scroller_box.remove(child)
                break
        self.merge_scroller_box.refresh()
    
    async def exe_merge(self, button):
        pass

def main():
    return PdfAutomated()
