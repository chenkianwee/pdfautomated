import io
from js import document, Uint8Array, File, URL
from pyodide.ffi.wrappers import add_event_listener

from pypdf import PdfReader, PdfWriter

MERGE_RES = None
EXT_RES = None
REDUCE_RES = None

def create_hidden_link(bstream: io.BytesIO, pdf_name: str):
    buffer = bstream.getbuffer()
    nbuffer = len(buffer)
    js_array = Uint8Array.new(nbuffer)
    js_array.assign(buffer)

    file = File.new([js_array], pdf_name, {type: "application/pdf"})
    url = URL.createObjectURL(file)

    hidden_link = document.createElement("a")
    hidden_link.setAttribute("download", f"{pdf_name}_download.pdf")
    hidden_link.setAttribute("href", url)
    hidden_link.click()

async def get_bytes_from_file(item) -> bytes:
    array_buf = await item.arrayBuffer()
    return array_buf.to_bytes()

def is_int(val: str):
    try: 
        int(val)
        return True
    except:
        return False

def merge_pdf(pdf_inputs: list[io.BytesIO]) -> io.BytesIO:
    merger = PdfWriter()

    for input in pdf_inputs:
        pdf = PdfReader(input)
        merger.append(pdf)
    merge_bstream = io.BytesIO()
    merger.write_stream(merge_bstream)
    return merge_bstream

def extract_pdf(pdf_input: io.BytesIO, ext_range: list[int]) -> io.BytesIO:
    pdf = PdfReader(pdf_input)
    start = ext_range[0]
    end = ext_range[1]
    writer = PdfWriter()
    for i in range(len(pdf.pages)):
        if start <= i+1 <= end:
            writer.add_page(pdf.pages[i])

    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    ext_bstream = io.BytesIO()
    writer.write_stream(ext_bstream)
    return ext_bstream

def reduce_pdf(pdf_input: io.BytesIO) -> io.BytesIO:
    pdf = PdfReader(pdf_input)
    writer = PdfWriter(clone_from=pdf)
    writer_reduce = PdfWriter()
    for page in writer.pages:
        page.compress_content_streams(level=9)
        writer_reduce.add_page(page)

    writer_reduce.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    reduce_bstream = io.BytesIO()
    writer_reduce.write_stream(reduce_bstream)
    return reduce_bstream

async def merge_file_and_show(e):
    try:
        file_input = document.querySelector("#merge-file-upload")
        file_list = file_input.files
        if len(file_list) > 0:
            bstream_ls = []
            for item in file_list:
                my_bytes: bytes = await get_bytes_from_file(item)
                bstream = io.BytesIO(my_bytes)
                bstream_ls.append(bstream)
            
            merge_bstream = merge_pdf(bstream_ls)
            global MERGE_RES
            MERGE_RES = merge_bstream
            output_div = document.querySelector("#merge-output")
            output_div.innerText = 'Successfully merged PDFs'
        else:
            output_div = document.querySelector("#merge-output")
            output_div.innerText = 'Please specify files to merge'
    except Exception as e:
        output_div = document.querySelector("#merge-output")
        output_div.innerText = str(e)

async def extract_file_and_show(e):
    try:
        file_input = document.querySelector("#ext-file-upload")
        file_list = file_input.files
        nfiles = len(file_list)
        item = file_list.item(0)
        st_val = document.querySelector("#ext-start").value
        end_val = document.querySelector("#ext-end").value
        is_st_int = is_int(st_val)
        is_end_int = is_int(end_val)
        if is_st_int == True and is_end_int == True and nfiles == 1:
            my_bytes: bytes = await get_bytes_from_file(item)
            bstream = io.BytesIO(my_bytes)
            ext_bstream = extract_pdf(bstream, [int(st_val),int(end_val)])
            global EXT_RES
            EXT_RES = ext_bstream
            output_div = document.querySelector("#ext-output")
            output_div.innerText = 'Successfully extracted PDF'
        else:
            output_div = document.querySelector("#ext-output")
            output_div.innerText = 'Please enter at least 1 PDF or valid integer for Start Page & End Page'
    except Exception as e:
        output_div = document.querySelector("#ext-output")
        output_div.innerText = str(e)

async def reduce_file_and_show(e):
    try:
        file_input = document.querySelector("#reduce-file-upload")
        file_list = file_input.files
        if len(file_list) == 1:
            item = file_list.item(0)
            my_bytes: bytes = await get_bytes_from_file(item)
            bstream = io.BytesIO(my_bytes)
            reduce_bstream = reduce_pdf(bstream)
            global REDUCE_RES
            REDUCE_RES = reduce_bstream
            output_div = document.querySelector("#reduce-output")
            output_div.innerText = 'Successfully reduced PDF'
        else:
            output_div = document.querySelector("#reduce-output")
            output_div.innerText = 'Please select at least 1 PDF file'
    except Exception as e:
        output_div = document.querySelector("#reduce-output")
        output_div.innerText = str(e)

def merge_downloadFile(*args):
    create_hidden_link(MERGE_RES, 'merge_pdf')

def ext_downloadFile(*args):
    create_hidden_link(EXT_RES, 'extracted_pdf')

def reduce_downloadFile(*args):
    create_hidden_link(REDUCE_RES, 'reduced_pdf')

add_event_listener(document.getElementById("merge-submit"), "click", merge_file_and_show)
add_event_listener(document.getElementById("ext-submit"), "click", extract_file_and_show)
add_event_listener(document.getElementById("reduce-submit"), "click", reduce_file_and_show)

add_event_listener(document.getElementById("merge-download"), "click", merge_downloadFile)
add_event_listener(document.getElementById("ext-download"), "click", ext_downloadFile)
add_event_listener(document.getElementById("reduce-download"), "click", reduce_downloadFile)