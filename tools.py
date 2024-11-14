import img2pdf
from pdf2docx import parse

def pdftodocx(pdf_path, docx_path):
    try:
        parse(pdf_path, docx_path)
    except Exception as ErrorText:
        print("pdf2docx Error:")
        print(ErrorText)
        pass

def image_to_pdf(filename, image):
    with open(filename, "wb") as pdf:
        pdf.write(img2pdf.convert(image))
