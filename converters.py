import os
import img2pdf
import pikepdf
import aspose.words as aw
import docx2pdf
import docx
from pypdf import PdfWriter
import file_utils
import pdf2image

def convert_images_to_pdf(user_folder, output_pdf):
    """
    Convert all images in a folder to a PDF.
    """
    A4_size = (img2pdf.mm_to_pt(210),img2pdf.mm_to_pt(297))
    layout_fun = img2pdf.get_layout_fun(A4_size)
    image_files = file_utils.list_files_by_time(user_folder)
    with open(output_pdf, "wb") as f:
        f.write(img2pdf.convert(image_files, layout_fun=layout_fun))
    return output_pdf

def convert_pdf_to_docx(pdf_path, output_docx):
    """
    Convert a PDF file to a DOCX file using Aspose.Words.
    """
    document = aw.Document(pdf_path)
    document.save(output_docx)
    os.remove(pdf_path)
    return output_docx

def convert_docx_to_pdf(docx_path, output_pdf):
    """
    Convert a DOCX file to PDF using docx2pdf.
    """
    docx2pdf.convert(docx_path, output_pdf)
    return output_pdf

def merge_pdfs(pdf_files, output_pdf):
    """
    Merge multiple PDF files into a single PDF.
    """
    merger = PdfWriter()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_pdf)
    merger.close()
    return output_pdf

def unlock_pdf(pdf_path):
    """
    Remove password restrictions from a PDF using pikepdf.
    """
    try:
        pdf = pikepdf.open(pdf_path)
        unlocked_path = f"{pdf_path}_Unlocked.pdf"
        pdf.save(unlocked_path)
        pdf.close()
        return unlocked_path
    except Exception as e:
        print(f"Error unlocking PDF: {e}")
        return None

def is_pdf_file(pdf_path):
    """Check if a file is a valid PDF."""
    if not pdf_path.endswith(".pdf"):
        return False
    try:
        pikepdf.open(pdf_path)
        return True
    except Exception:
        return False

def is_docx_file(docx_path):
    """Check if a file is a valid DOCX file."""
    try:
        docx.Document(docx_path)
        return True
    except Exception:
        return False

def convert_pdf_to_image(user_folder, pdf_path):
    """
    Convert pdf pages to image and save in user_folder path.
    """
    pages = pdf2image.convert_from_path(pdf_path)
    for page in pages:
        random_name = file_utils.random_name()
        image_path = f"{user_folder}/{random_name}.jpg"
        page.save(image_path, "JPEG")
    os.remove(pdf_path)
    return file_utils.list_files_by_time(user_folder)

