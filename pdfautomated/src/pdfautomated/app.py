"""
Tool for merg size
"""
import io
import sys
import asyncio
import subprocess
from pathlib import Path
from typing import Callable

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import aiofiles
from pypdf import PdfReader, PdfWriter

class PdfAutomated(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.grid_marginx = 1
        self.grid_marginy = 5  
        style_pack_header = Pack(text_align='center', font_weight='bold', font_size=10, background_color='rgba(125, 125, 125, 0.2)', 
                                 color='black')
        # region: merge tab
        # merge tab parameters
        self.nmerge = 0
        self.merge_txt_dict = {}
        self.merge_row_id = 'merge_row_'
        self.merge_txt_id = 'merge_text_'
        self.merge_btn_id = 'merge_btn_'
        self.merge_addbtn_id = 'merge_addbtn_0'
        self.merge_rmbtn_id = 'merge_rmbtn_'
        self.merge_res = None
        self.sel_merge_res_btn_id = 'merge_res_sel_btn'
        self.show_merge_res_btn_id = 'merge_res_show_btn'
        # Merge tab
        self.init_gui('merge', 2, self.merge_addbtn_id, self.exe_merge)
        # endregion: merge tab
        
        # region: extract tab
        self.nextract = 0
        self.extract_txt_dict = {}
        self.extract_row_id = 'extract_row_'
        self.extract_row_id2 = 'extract_row2_'
        self.extract_col_id = 'extract_col_'
        self.extract_txt_id = 'extract_text_'
        self.extract_btn_id = 'extract_btn_'
        self.extract_addbtn_id = 'extract_addbtn_0'
        self.extract_rmbtn_id = 'extract_rmbtn_'
        self.extract_res = None
        self.sel_extract_res_btn_id = 'extract_res_sel_btn'
        self.show_extract_res_btn_id = 'extract_res_show_btn'
        # Extract tab
        self.init_gui('extract', 1, self.extract_addbtn_id, self.exe_extract)
        # endregion: extract tab
        
        # region: reduce tab
        # reduce tab parameters
        self.nreduce = 0
        self.reduce_txt_dict = {}
        self.reduce_row_id = 'reduce_row_'
        self.reduce_txt_id = 'reduce_text_'
        self.reduce_btn_id = 'reduce_btn_'
        self.reduce_addbtn_id = 'reduce_addbtn_0'
        self.reduce_rmbtn_id = 'reduce_rmbtn_'
        self.reduce_res = None
        self.sel_reduce_res_btn_id = 'reduce_res_sel_btn'
        self.show_reduce_res_btn_id = 'reduce_res_show_btn'
        # reduce tab
        self.init_gui('reduce', 1, self.reduce_addbtn_id, self.exe_reduce)
        # endregion: reduce tab
        
        # tab container
        tabs_container = toga.OptionContainer(flex=1,
                                              style=Pack(margin=(10, 10), align_items='center'),
                                              content=[toga.OptionItem("MergePDF", self.merge_tab),
                                                       toga.OptionItem("ExtractPDF", self.extract_tab),
                                                       toga.OptionItem("ReducePDF", self.reduce_tab)])
        # main box
        main_box = toga.Box(style=Pack(align_items='center'))
        main_box.add(tabs_container)
        # main window
        self.main_window = toga.MainWindow(title=self.formal_name, size=(900, 800))
        self.main_window.content = main_box
        self.main_window.show()
    
    def init_gui(self, mode: str, ninit: int, addbtn_id: str, exe_func: Callable):
        scroller_box = toga.Box(direction=COLUMN)
        for _ in range(ninit):
            file_selector = self.add_a_row(mode)
            scroller_box.add(file_selector)
            if mode == 'merge':
                self.nmerge+=1
            elif mode == 'extract':
                self.nextract+=1
            elif mode == 'reduce':
                self.nreduce+=1

        btn_box = toga.Box(flex=0, direction=COLUMN, margin=(self.grid_marginy, self.grid_marginx))
        add_button = toga.Button("+", id=addbtn_id, on_press=self.add_a_row_user, margin=(self.grid_marginy, self.grid_marginx))
        res_row = self.add_a_res_row(mode)
        exe_btn = toga.Button("Execute", on_press=exe_func, margin=(self.grid_marginy, self.grid_marginx))
        btn_box.add(add_button)
        btn_box.add(res_row)
        btn_box.add(exe_btn)
        
        # structure the GUI
        scroller = toga.ScrollContainer(
            horizontal=True,
            vertical=True,
            flex=1,
            margin=10
            )
        
        scroller.content = scroller_box
        tab = toga.Box(direction=COLUMN)
        tab.add(scroller)
        tab.add(btn_box)
        
        if mode == 'merge':
            self.merge_scroller_box = scroller_box
            self.add_merge_button = add_button
            self.merge_res_row = res_row
            self.exe_merge_button = exe_btn
            self.merge_scroller = scroller
            self.merge_tab = tab
        elif mode == 'extract':
            self.extract_scroller_box = scroller_box
            self.add_extract_button = add_button
            self.extract_res_row = res_row
            self.exe_extract_button = exe_btn
            self.extract_scroller = scroller
            self.extract_tab = tab
        elif mode == 'reduce':
            self.reduce_scroller_box = scroller_box
            self.add_reduce_button = add_button
            self.reduce_res_row = res_row
            self.exe_reduce_button = exe_btn
            self.reduce_scroller = scroller
            self.reduce_tab = tab

    def add_a_res_row(self, mode: str) -> toga.Box:
        """
        Create a box containing a row box with all the widgets for selecting where to save your result file 
        
        Parameters
        ----------
        mode : str
            'merge', 'extract', 'reduce'. 
            
        Returns
        -------
        res_box : toga.Box
            box containing a row box with all the widgets for selecting where to save your result file
        """
        def basic_res_row(label: str, sel_btn_id: str, open_btn_id: str, mode: str):
            row_box = toga.Box(flex=0, direction=ROW, margin=(self.grid_marginy, self.grid_marginx))
            res_label = toga.Label(label, margin=(self.grid_marginy, self.grid_marginx), style=Pack(text_align='center'))
            res_val = toga.TextInput(flex=1, readonly=True, margin=(self.grid_marginy, self.grid_marginx))
            res_val.enabled = False

            select_button = toga.Button("Select", id = sel_btn_id, on_press=self.select_resfile, margin=(self.grid_marginy, self.grid_marginx))
            open_button = toga.Button("Show", id=open_btn_id, on_press=self.open_folder, margin=(self.grid_marginy, self.grid_marginx))
            
            row_box.add(res_label)
            row_box.add(res_val)
            row_box.add(select_button)
            row_box.add(open_button)
            if mode == 'merge':
                self.merge_res = res_val
            elif mode == 'extract':
                self.extract_res = res_val
            elif mode == 'reduce':
                self.reduce_res = res_val
            return row_box
        
        if mode == 'merge':
            sel_btn_id = self.sel_merge_res_btn_id
            open_btn_id = self.show_merge_res_btn_id
            label = 'Result File Path'
        
        if mode == 'extract':
            sel_btn_id = self.sel_extract_res_btn_id
            open_btn_id = self.show_extract_res_btn_id
            label = 'Result Folder Path'

        if mode == 'reduce':
            sel_btn_id = self.sel_reduce_res_btn_id
            open_btn_id = self.show_reduce_res_btn_id
            label = 'Result Folder Path'

        row_box = basic_res_row(label, sel_btn_id, open_btn_id, mode)
        return row_box

    async def select_resfile(self, button):
        if button.id == self.sel_merge_res_btn_id:
            path_name = await self.main_window.dialog(
                toga.SaveFileDialog(title='Save to', suggested_filename = 'merge_result.pdf'))
            self.merge_res.value = path_name

        elif button.id == self.sel_extract_res_btn_id:
            path_name = await self.main_window.dialog(
                toga.SelectFolderDialog(title='Save to'))
            self.extract_res.value = path_name
        
        elif button.id == self.sel_reduce_res_btn_id:
            path_name = await self.main_window.dialog(
                toga.SelectFolderDialog(title='Save to'))
            self.reduce_res.value = path_name

    def add_a_row(self, mode: str) -> toga.Box:
        def row_basic(path_val_id, txt_dict, sel_btn_id, on_press_func, row_box_id):
            label = toga.Label('Select a PDF', margin=(self.grid_marginy, self.grid_marginx), style=Pack(text_align='center'))
            path_val = toga.TextInput(flex=1, id = path_val_id, readonly=True, margin=(self.grid_marginy, self.grid_marginx))
            path_val.enabled = False
            txt_dict[path_val_id] = path_val
            select_button = toga.Button("Select", id = sel_btn_id, on_press=on_press_func, margin=(self.grid_marginy, self.grid_marginx))
            row_box = toga.Box(flex=0, id = row_box_id, direction=ROW, margin=(self.grid_marginy, self.grid_marginx))
            row_box.add(label)
            row_box.add(path_val)
            row_box.add(select_button)
            return row_box
        
        if mode == 'merge':
            path_val_id = f"{self.merge_txt_id}{self.nmerge}"
            row_box_id = f"{self.merge_row_id}{self.nmerge}"
            txt_dict = self.merge_txt_dict
            sel_btn_id = f"{self.merge_btn_id}{self.nmerge}"
            on_press_func = self.select_file
            row_box = row_basic(path_val_id, txt_dict, sel_btn_id, on_press_func, row_box_id)
            return row_box
        
        elif mode == 'extract':
            path_val_id = f"{self.extract_txt_id}{self.nextract}"
            row_box_id = f"{self.extract_row_id}{self.nextract}"
            txt_dict = self.extract_txt_dict
            sel_btn_id = f"{self.extract_btn_id}{self.nextract}"
            on_press_func = self.select_file
            row_box = row_basic(path_val_id, txt_dict, sel_btn_id, on_press_func, row_box_id)
            
            start_label = toga.Label('Start Page', margin=(self.grid_marginy, self.grid_marginx), style=Pack(text_align='center'))
            end_label = toga.Label('End Page', margin=(self.grid_marginy, self.grid_marginx), style=Pack(text_align='center'))
            start_val = toga.NumberInput(flex=1, margin=(self.grid_marginy, self.grid_marginx))
            end_val = toga.NumberInput(flex=1, margin=(self.grid_marginy, self.grid_marginx))
            row_box2 = toga.Box(flex=0, id = f"{self.extract_row_id2}{self.nextract}", direction=ROW, margin=(self.grid_marginy, self.grid_marginx))
            row_box2.add(start_label)
            row_box2.add(start_val)
            row_box2.add(end_label)
            row_box2.add(end_val)
            
            divider = toga.Divider(style=Pack(margin=(self.grid_marginy, self.grid_marginx), height=2))
    
            col_box = toga.Box(flex=0, id=f"{self.extract_col_id}{self.nextract}", direction=COLUMN, margin=(self.grid_marginy, self.grid_marginx))
            col_box.add(divider)
            col_box.add(row_box)
            col_box.add(row_box2)
            
            return col_box
        
        if mode == 'reduce':
            path_val_id = f"{self.reduce_txt_id}{self.nreduce}"
            row_box_id = f"{self.reduce_row_id}{self.nreduce}"
            txt_dict = self.reduce_txt_dict
            sel_btn_id = f"{self.reduce_btn_id}{self.nreduce}"
            on_press_func = self.select_file
            row_box = row_basic(path_val_id, txt_dict, sel_btn_id, on_press_func, row_box_id)
            return row_box

    def add_a_row_user(self, button):
        btn_split = button.id.split('_')
        btn_type = btn_split[0]
        if btn_type == 'merge':
            row_box = self.add_a_row(btn_type)
            rm_btn_id = f"{self.merge_rmbtn_id}{self.nmerge}"
            scroller_box = self.merge_scroller_box
            self.nmerge+=1
        
        elif btn_type == 'extract':
            row_box = self.add_a_row(btn_type)
            rm_btn_id = f"{self.extract_rmbtn_id}{self.nextract}"
            scroller_box = self.extract_scroller_box
            self.nextract+=1

        elif btn_type == 'reduce':
            row_box = self.add_a_row(btn_type)
            rm_btn_id = f"{self.reduce_rmbtn_id}{self.nreduce}"
            scroller_box = self.reduce_scroller_box
            self.nreduce+=1

        rm_button = toga.Button("Remove", id = rm_btn_id, on_press=self.rm_row_user, margin=(self.grid_marginy, self.grid_marginx))
        row_box.add(rm_button)

        nchildren = len(scroller_box.children)
        scroller_box.insert(nchildren, row_box)

    def rm_row_user(self, button):
        btn_split = button.id.split('_')
        btn_type = btn_split[0]
        btn_cnt = btn_split[2]
        if btn_type == 'merge':
            scroller_box = self.merge_scroller_box
            row_id_ref = f"{self.merge_row_id}{btn_cnt}"
        
        if btn_type == 'extract':
            scroller_box = self.extract_scroller_box
            row_id_ref = f"{self.extract_col_id}{btn_cnt}"

        if btn_type == 'reduce':
            scroller_box = self.reduce_scroller_box
            row_id_ref = f"{self.reduce_row_id}{btn_cnt}"

        children = scroller_box.children
        for child in children:
            row_id = child.id
            if row_id == row_id_ref:
                scroller_box.remove(child)
                break
        scroller_box.refresh()

    async def select_file(self, button):
        btn_split = button.id.split('_')
        btn_type = btn_split[0]
        btn_cnt = btn_split[2]

        if btn_type == 'merge':
            txt_dict = self.merge_txt_dict
            txt_id = f"{self.merge_txt_id}{btn_cnt}"

        elif btn_type == 'extract':
            txt_dict = self.extract_txt_dict
            txt_id = f"{self.extract_txt_id}{btn_cnt}"

        elif btn_type == 'reduce':
            txt_dict = self.reduce_txt_dict
            txt_id = f"{self.reduce_txt_id}{btn_cnt}"

        path_name = await self.main_window.dialog(
            toga.OpenFileDialog(title='Select PDF for Processing'))
        txt_dict[txt_id].value = path_name
    
    def extract_parms(self, mode: str) -> list:
        """
        Extract the parameters 
        
        Parameters
        ----------
        mode : str
            'merge', 'extract', 'reduce'. 
            
        Returns
        -------
        res_parms : list
            extracted parameter values
        """
        if mode == 'merge':
            children = self.merge_scroller_box.children
            merge_file_ls = []
            for child in children:
                children2 = child.children
                for child2 in children2:
                    if type(child2) == toga.TextInput:
                        merge_file_ls.append(child2.value)
                        break

            return merge_file_ls
        
        elif mode == 'extract':
            children = self.extract_scroller_box.children
            extract_file_ls = []
            start_stop_ls = []
            for child in children:
                filepath = child.children[1].children[1].value
                start = child.children[2].children[1].value
                end = child.children[2].children[3].value
                extract_file_ls.append(filepath)
                start_stop_ls.append([start, end])

            return [extract_file_ls, start_stop_ls]
        
        elif mode == 'reduce':
            children = self.reduce_scroller_box.children
            reduce_file_ls = []
            for child in children:
                children2 = child.children
                for child2 in children2:
                    if type(child2) == toga.TextInput:
                        reduce_file_ls.append(child2.value)
                        break

            return reduce_file_ls
        
    async def open_folder(self, button):
        if button.id == self.show_merge_res_btn_id:
            file_path = self.merge_res.value
            if file_path:
                folder_path = str(Path(file_path).parent)
            else:
                folder_path = ''

        elif button.id == self.show_extract_res_btn_id:
            folder_path = self.extract_res.value
        
        elif button.id == self.show_reduce_res_btn_id:
            folder_path = self.reduce_res.value

        if folder_path:
            try:
                if sys.platform == 'win32':
                    subprocess.Popen(['explorer', folder_path], start_new_session=True)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', folder_path], start_new_session=True)
                else:  # For Linux
                    subprocess.Popen(['xdg-open', folder_path], start_new_session=True)
            except Exception as e:
                await self.main_window.dialog(
                    toga.ErrorDialog(
                            'Error',
                            f"Error opening folder: {e}",
                        )
                    )
        else:
            await self.main_window.dialog(
                toga.ErrorDialog(
                        'Error',
                        "Please specify folder!",
                    )
                )
    
    def reset_gui(self, mode: str):
        """
        Reset the gui
        
        Parameters
        ----------
        mode : str
            'merge', 'extract', 'reduce'.
        """
        if mode == 'merge':
            self.add_merge_button.enabled = True
            self.exe_merge_button.enabled = True
            self.merge_progress.stop()
            self.merge_progress.value = 0
            self.merge_tab.remove(self.merge_progress)
        elif mode == 'extract':
            self.add_extract_button.enabled = True
            self.exe_extract_button.enabled = True
            self.extract_progress.stop()
            self.extract_progress.value = 0
            self.extract_tab.remove(self.extract_progress)
        elif mode == 'reduce':
            self.add_reduce_button.enabled = True
            self.exe_reduce_button.enabled = True
            self.reduce_progress.stop()
            self.reduce_progress.value = 0
            self.reduce_tab.remove(self.reduce_progress)

    async def read_pdf(self, pdf_path: str):
        async with aiofiles.open(pdf_path, 'rb') as file:
            content = await file.read()
            bstream = io.BytesIO(content)
            return bstream

    async def exe_merge(self, button):
        try:
            # disable all the buttons
            self.add_merge_button.enabled = False
            self.exe_merge_button.enabled = False
            # progress bar
            self.merge_progress = toga.ProgressBar(max=100, value=0)
            self.merge_tab.add(self.merge_progress)
            self.merge_progress.value = 10

            error_msgs = ''
            merge_file_ls = self.extract_parms('merge')
            self.merge_progress.value = 20
            fcnt = 0
            for fstr in merge_file_ls:
                if fstr:
                    fcnt+=1

            if fcnt < 2:
                error_msgs+='Please specify at least 2 PDF files for merging\n'

            # get the path for the res file
            res_filepath = self.merge_res.value
            if not res_filepath:
                error_msgs+='Please specify result filepath\n'

            if error_msgs:
                    await self.main_window.dialog(
                            toga.ErrorDialog(
                                    'Error',
                                    error_msgs,
                                )
                            )
                    self.reset_gui('merge')
                    return None
            
            writer = PdfWriter()
            # Read all PDFs asynchronously

            tasks = []
            for path in merge_file_ls:
                task = asyncio.create_task(self.read_pdf(path))
                tasks.append(task)
            
            pdf_contents = await asyncio.gather(*tasks)
            self.merge_progress.value = 50
            # Merge PDFs
            for content in pdf_contents:
                reader = PdfReader(content)
                writer.append(reader)
            self.merge_progress.value = 70
            
            writer.write(res_filepath)
            writer.close()

            self.merge_progress.value = 100
            await self.main_window.dialog(
                        toga.InfoDialog(
                                'Success!',
                                'The merging has been completed!',
                            )
                        )
            self.reset_gui('merge')

        except Exception as e:
            await self.main_window.dialog(
                        toga.ErrorDialog(
                                'Error',
                                f"Error occured:\n {e}",
                            )
                        )
            self.reset_gui('merge')

    async def exe_extract(self, button):
        try:
            # disable all the buttons
            self.add_extract_button.enabled = False
            self.exe_extract_button.enabled = False
            # progress bar
            self.extract_progress = toga.ProgressBar(max=100, value=0)
            self.extract_tab.add(self.extract_progress)
            self.extract_progress.value = 10

            error_msgs = ''
            parm_ls = self.extract_parms('extract')
            file_ls = parm_ls[0]
            se_ls = parm_ls[1]
            self.extract_progress.value = 20
            fcnt = 0
            for fstr in file_ls:
                if fstr:
                    fcnt+=1

            if fcnt < 1:
                error_msgs+='Please specify at least 1 PDF files for extraction\n'

            # get the path for the res file
            res_filepath = self.extract_res.value
            if not res_filepath:
                error_msgs+='Please specify result filepath\n'

            if error_msgs:
                    await self.main_window.dialog(
                            toga.ErrorDialog(
                                    'Error',
                                    error_msgs,
                                )
                            )
                    self.reset_gui('extract')
                    return None
            
            # Read all PDFs asynchronously

            tasks = []
            for path in file_ls:
                task = asyncio.create_task(self.read_pdf(path))
                tasks.append(task)
            
            pdf_contents = await asyncio.gather(*tasks)
            self.extract_progress.value = 50
            npdf = len(pdf_contents)
            # Extract PDFs
            for cnt, content in enumerate(pdf_contents):
                reader = PdfReader(content)
                filename_ext = Path(file_ls[cnt]).name
                filename_split = str(filename_ext).split('.')
                if len(filename_split) > 2:
                    filename = ''
                    for fn in filename_split:
                        filename += fn
                else:
                    filename = filename_split[0]
                start = se_ls[cnt][0]
                end = se_ls[cnt][1]
                writer = PdfWriter()
                for i in range(len(reader.pages)):
                    if start <= i+1 <= end:
                        writer.add_page(reader.pages[i])

                writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

                pdf_res_filepath = Path(res_filepath).joinpath(f'{filename}_{start}_{end}.pdf')
                writer.write(pdf_res_filepath)
                writer.close()
                self.extract_progress.value = (cnt/npdf*50) + 50
            
            self.extract_progress.value = 100
            
            await self.main_window.dialog(
                        toga.InfoDialog(
                                'Success!',
                                'The extraction has been completed!',
                            )
                        )
            self.reset_gui('extract')

        except Exception as e:
            await self.main_window.dialog(
                        toga.ErrorDialog(
                                'Error',
                                f"Error occured:\n {e}",
                            )
                        )
            self.reset_gui('extract')
    
    async def exe_reduce(self, button):
        try:
            # disable all the buttons
            self.add_reduce_button.enabled = False
            self.exe_reduce_button.enabled = False
            # progress bar
            self.reduce_progress = toga.ProgressBar(max=100, value=0)
            self.reduce_tab.add(self.reduce_progress)
            self.reduce_progress.value = 10

            error_msgs = ''
            file_ls = self.extract_parms('reduce')
            self.reduce_progress.value = 20
            fcnt = 0
            for fstr in file_ls:
                if fstr:
                    fcnt+=1

            if fcnt < 1:
                error_msgs+='Please specify at least 1 PDF files for reduction\n'

            # get the path for the res file
            res_filepath = self.reduce_res.value
            if not res_filepath:
                error_msgs+='Please specify result filepath\n'

            if error_msgs:
                    await self.main_window.dialog(
                            toga.ErrorDialog(
                                    'Error',
                                    error_msgs,
                                )
                            )
                    self.reset_gui('reduce')
                    return None
            
            # Read all PDFs asynchronously

            tasks = []
            for path in file_ls:
                task = asyncio.create_task(self.read_pdf(path))
                tasks.append(task)
            
            pdf_contents = await asyncio.gather(*tasks)
            self.reduce_progress.value = 50
            npdf = len(pdf_contents)
            # Extract PDFs
            for cnt, content in enumerate(pdf_contents):
                reader = PdfReader(content)
                filename_ext = Path(file_ls[cnt]).name
                filename_split = str(filename_ext).split('.')
                if len(filename_split) > 2:
                    filename = ''
                    for fn in filename_split:
                        filename += fn
                else:
                    filename = filename_split[0]
                
                writer = PdfWriter()
                for i in range(len(reader.pages)):
                    writer.add_page(reader.pages[i])

                writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

                pdf_res_filepath = Path(res_filepath).joinpath(f'{filename}_reduced.pdf')
                writer.write(pdf_res_filepath)
                writer.close()
                self.reduce_progress.value = (cnt/npdf*50) + 50
            
            self.reduce_progress.value = 100
            
            await self.main_window.dialog(
                        toga.InfoDialog(
                                'Success!',
                                'The reduction has been completed!',
                            )
                        )
            self.reset_gui('reduce')

        except Exception as e:
            await self.main_window.dialog(
                        toga.ErrorDialog(
                                'Error',
                                f"Error occured:\n {e}",
                            )
                        )
            self.reset_gui('reduce')

def main():
    return PdfAutomated()
