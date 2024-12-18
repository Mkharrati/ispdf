import img2pdf
import random
import pikepdf
from pdf2docx import parse

def random_name():
    txt = "0123456789"
    name = "".join(random.sample(txt, 9))
    return name


def tools(pdf_path, docx_path):
    try:
        parse(pdf_path, docx_path)
    except Exception as ErrorText:
        print("pdf2docx Error:")
        print(ErrorText)
        pass

def image_to_pdf(image):
    file_name = random_name()+".pdf"
    with open(file_name, "wb") as pdf:
        pdf.write(img2pdf.convert(image))
    return file_name

def Unlock(pdf):
    file = pikepdf.open(pdf)
    file.save("Unlocked_"+pdf)
    return file



class Message_Details:
    def __init__(self, message):
        self.message = message
    
    def file_id(self):

        message = self.message.json

        if ("photo" in message):
            return message["photo"][-1]["file_id"]

        elif ("document" in message):
            return message["document"]["file_id"]
        
        else:
            print("content_types not found")
        
    
    def file_path(self):

        message = self.message.json

        if ("photo" in message):
            print (message["photo"])

        elif ("document" in message):
            return message["document"][0]["file_path"]
        
        else:
            print("content_types not found")


    

        