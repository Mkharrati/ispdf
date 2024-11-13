from pdf2docx import parse

def pdftodocx(pdf_path, docx_path):
    try:
        parse(pdf_path, docx_path)
    except Exception as ErrorText:
        print("pdf2docx Error:")
        print(ErrorText)
        pass