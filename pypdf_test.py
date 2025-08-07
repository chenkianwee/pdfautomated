from pypdf import PdfReader, PdfWriter
from pathlib import Path

# pdf_path = '/home/chenkianwee/kianwee_work/code_workspace/26.pdfautomated/yun2inf_vision.pdf'
# pdf_path = '/home/chenkianwee/kianwee_work/get/2025_07_to_2025_12/jpn_visit/pdf/research_overview.pdf'
pdf_path = '/home/chenkianwee/kianwee_work/code_workspace/26.pdfautomated/luis gama caldas.pdf'
pdf_res_dirpath = '/home/chenkianwee/kianwee_work/code_workspace/26.pdfautomated'
reader = PdfReader(pdf_path)
number_of_pages = len(reader.pages)
page = reader.pages[0]
text = page.extract_text()
# split pdf 
def split_pdf(input_path: str, split_range: list[int]):
    pdf = PdfReader(input_path)
    start = split_range[0]
    end = split_range[1]
    writer = PdfWriter()
    for i in range(len(pdf.pages)):
        if start <= i+1 <= end:
            writer.add_page(pdf.pages[i])

    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    pdf_res_filepath = Path(pdf_res_dirpath).joinpath(f'output_{start}_{end}.pdf')
    with open(pdf_res_filepath, 'wb') as output_file:
        writer.write(output_file)
# split_pdf(pdf_path, [1,2])

# merge pdf
def merge_pdf(input_paths: list[str]):
    merger = PdfWriter()

    for pdf in input_paths:
        merger.append(pdf)

    pdf_res_filepath = Path(pdf_res_dirpath).joinpath(f'output_merged.pdf')
    merger.write(pdf_res_filepath)
    merger.close()

merge_pdf_ls = ['/home/chenkianwee/kianwee_work/code_workspace/26.pdfautomated/output_1_5.pdf', 
                '/home/chenkianwee/kianwee_work/code_workspace/26.pdfautomated/output_6_10.pdf',
                '/home/chenkianwee/kianwee_work/code_workspace/26.pdfautomated/output_11_17.pdf']

# merge_pdf(merge_pdf_ls)

# compress pdf
def reduce_pdf(pdf_path: str, lossless_compression: int = 9):
    pdf = PdfReader(pdf_path)
    npages = len(pdf.pages)

    writer = PdfWriter()
    for i in range(npages):
        writer.add_page(pdf.pages[i])
   
    for page in writer.pages:
        page.compress_content_streams(level=9)  # This is CPU intensive!

    writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    pdf_res_filepath = Path(pdf_res_dirpath).joinpath(f'output_compressed1.pdf')
    with open(pdf_res_filepath, "wb") as f:
        writer.write(f)

reduce_pdf(pdf_path)
# split_pdf(pdf_path, [1,61])