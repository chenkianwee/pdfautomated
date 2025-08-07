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
        # content_box = toga.Box()
        main_box = toga.Box()
        # create a box to contain all the parameters
        grid_marginx = 1
        grid_marginy = 5  
        style_pack_header = Pack(text_align='center', font_weight='bold', font_size=10, background_color='rgba(125, 125, 125, 0.2)', 
                                 color='black')
        default_path = '/home/chenkianwee/kianwee_work/code_workspace/26.pdfautomated/luis gama caldas.pdf'
        save_row_box = toga.Box(flex=1, direction=ROW, margin=(grid_marginy, grid_marginx))
        self.path_val = toga.TextInput(value=default_path, flex=1, readonly=True, margin=(grid_marginy, grid_marginx))
        # self.path_val.enabled = False
        self.select_button = toga.Button("Select", on_press=self.select_file, margin=(grid_marginy, grid_marginx))
        save_row_box.add(self.path_val)
        save_row_box.add(self.select_button)
        main_box.add(save_row_box)
        # main box
        
        # main_box.add(content_box)
        # main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    async def select_file(self, widget):
        pdf = PdfReader(self.path_val.value)
        npages = len(pdf.pages)
        await self.main_window.dialog(
            toga.InfoDialog(
                f"Hello, this pdf have {npages}",
                "Hi there!",
            )
        )

def main():
    return PdfAutomated()
