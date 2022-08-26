''' Solved
'''
from io import BytesIO

import json
import re
import pytesseract

from PIL import Image
from pdf2image import convert_from_path
import xml.etree.ElementTree as ET


pages = convert_from_path(pdf_path='file.pdf', fmt='jpeg', dpi=300)

for pageIndex, page in enumerate(pages):
    current_file = BytesIO()

    if pageIndex == 0:
        page.save(current_file, 'JPEG')
        ocr_text = pytesseract.image_to_string(image=Image.open(current_file))

        NFES_SP_PATTERN = (
            '.*SAO\sPAULO\s(.+|[0-9]+)\s+[a-zA-Z\s]+.*'
            '([0-9]{2}\/[0-9]{2}\/[0-9]{4})\s([0-9]+\:[0-9]+:[0-9]+)\s+.*\s+'
            'RPS\sN.\s([0-9])+\sSérie\s([0-9]+).+[0-9]{2}\/[0-9]{2}\/[0-9]{4}'
            '\s(.+\-.+)\s+[A-Z\s]+'
            'CPF\/CNPJ:\s([0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2})'
            '\sInscri.{2}o Municipal:\s([0-9]{1}\.[0-9]{3}\.[0-9]{3}-[0-9]{1})'
            '\sNome\/Razao Social:\s([A-Z\s]+)\s'
            'Endere.o:\s([a-zA-Z]+)\s([A-Z0-9\s]+)\s'
            '([A-Z0-9\s]+),\s([a-zA-Z0-9\s]+)\s-\s([a-zA-Z0-9\s]+)\s'
            '-\sCEP:\s([0-9]{5}-[0-9]{3})\s'
            'Municipio:\s(.+)\sUF:\s([A-Z]{2})\s+.+\s+'
            'Nome\/Razao Social:\s([A-Z\s]+)\s'
            'CPF\/CNPJ:\s([0-9]{2}\.[0-9]{3}\.[0-9]{3}\/[0-9]{4}-[0-9]{2})\s'
            'Inscri.{2}o Municipal:\s(-+)\sEndere.o:\s([a-zA-Z]+)\s([A-Z0-9\s]+)'
            '\s([A-Z0-9\s]+),\s([a-zA-Z0-9\s]+)\s-\s([a-zA-Z0-9\s]+)\s-\s'
            'CEP:\s([0-9]{5}-[0-9]{3})\sMunicipio:\s(.+)\sUF:\s([A-Z]{2})\s'
            'E-mail:(.*)\s+.+\s.+\s+DISCRIMINACAO DOS SERVICOS\s((.+|\n)+?)\s+'
            'VALOR TOTAL DO SERVICO = R\$\s([0-9\.\,]+)'
            )

        nfes_data = re.findall(pattern=NFES_SP_PATTERN, string=ocr_text)[0]

        address_prestador = {
            'TipoLogradouro': nfes_data[9],
            'Logradouro': nfes_data[10],
            'NumeroEndereco': nfes_data[11],
            'ComplementoEndereco': nfes_data[12],
            'Bairro': nfes_data[13],
            'Cidade': nfes_data[14],
            'UF': nfes_data[15],
            'CEP': nfes_data[16]
        }

        address_tomador = {
            'TipoLogradouro': 'RUA',
            'Logradouro': nfes_data[20] + ' ' + nfes_data[21],
            'NumeroEndereco': nfes_data[22],
            'ComplementoEndereco': nfes_data[23],
            'Bairro': nfes_data[24],
            'Cidade': nfes_data[26],
            'UF': nfes_data[27],
            'CEP': nfes_data[25],
            'Email': nfes_data[28]
        }

        print(address_tomador)
