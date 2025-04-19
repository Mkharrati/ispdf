import requests
import json

OCR_URL = "https://www.eboo.ir/api/ocr/getway"

def send_file(file_path, OCR_TOKEN):
    """
    send file to ocr server. return json_data.
    
    json_data sample :
    {
        "Status":"Done",
        "PageCount":"42",
        "FileToken":"Nzrwxxxxxxxx4f3e5",
        "ConvertMethods":"1,2,3,4"
    }
    """
    file_name = file_path
    upload = {'filehandle':(file_name, open(file_name, 'rb'), 'multipart/form-data')}
    payload = {
    "token": OCR_TOKEN,
    "command": "addfile",
    }
    try:
        response = requests.post(OCR_URL, data=payload, files=upload)
        data = response.text
        json_data = json.loads(data)
    except Exception as error:
        return ("False", error)
    print(f"{file_name} sent to server successfully")
    return json_data
    

def pdf_to_docx(file_token, OCR_TOKEN, method = 1):
    """
    Convert pdf to docx (on the server) via file_token. return docx_url.

    json_data sample :
    {
        "Status":"Done",
        " FileToDownload ":
        "https://www.eboo.ir/APIDownloader/OCRAPI/OutputFile.Docx"
    }
    """
    payload = {
    "token": OCR_TOKEN,
    "command": "convert",
    "filetoken": file_token,
    "method": method
    }
    docx_url = ""
    try:
        response = requests.post(OCR_URL, data=payload)
        data = response.text
        json_data = json.loads(data)
        docx_url = json_data["FileToDownload"]
    except Exception as error:
        return ("False", error)
    return docx_url

def image_to_text(file_token, OCR_TOKEN):
    """extract texts from image (on the server) via file_token. return text"""
    payload = {
    "token": OCR_TOKEN,
    "command": "convert",
    "filetoken": file_token,
    "output": "txtraw",
    "method": 4
    }
    try:
        response = requests.post(OCR_URL, data=payload)
        extracted_text = response.text
    except Exception as error:
        return ("False", error)
    return extracted_text

def delete_file(file_token, OCR_TOKEN):
    """
    delete file from the server via file_token.
    """
    payload = {
    "token": OCR_TOKEN,
    "command": "deletefile",
    "filetoken": file_token,
    }
    try:
        response = requests.post(OCR_URL, data=payload)
        print(f"{file_token} deleted")
        data = response.text
        json_data = json.loads(data)
        if "DeleteDone" not in json_data["Status"]:
            return ("False", json_data)
    except Exception as error:
        return ("False", error)
    return data