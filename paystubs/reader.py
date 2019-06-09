from PyPDF2 import PdfFileReader

class AcmePaystubReader:
    text = ''

    def __init__(self, io):
        self.reader = PdfFileReader(io)
        for page_num in range(self.reader.numPages):
            page = self.reader.getPage(page_num)
            self.text += page.extractText()

