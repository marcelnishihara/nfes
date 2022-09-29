'''Solved
'''
import re

from nfes.nota_fiscal_sp import NotaFiscalSP


files = []

for index, pdf_path in enumerate(files):
    nfes = NotaFiscalSP(pdf_path=pdf_path)
    ocr_text = nfes.extract_data()
    nfes.compose_nfes_data()
    nfes.compose_service_provider_data()
    nfes.compose_taker_data()
    nfes.compose_service_data()

    file_name = re.findall(pattern=r'(.*)\.pdf', string=pdf_path)[0]
    nfes.log(file_name=f'{file_name}')
