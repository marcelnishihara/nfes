'''NotaFiscalSP
'''
from datetime import datetime
from io import BytesIO
from xml.etree.ElementTree import Element, ElementTree, SubElement

import re
import pytesseract

from PIL import Image
from pdf2image import convert_from_path


class NotaFiscalSP:
    '''Solved
    '''

    def __init__(
        self, pdf_path: str, img_extension: str = 'jpeg', dpi: int = 300
        ) -> None:
        '''Solved
        '''
        self.pdf_first_page = convert_from_path(
            pdf_path=pdf_path, fmt=img_extension, dpi=dpi)[0]

        self.pdf_file = BytesIO()
        self.ocr_text = ''
        self.nfes_data = ()

        self.xml = Element('NFe', xmlns='')


        self.nfes_sp_pattern = (
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
            'VALOR TOTAL DO SERVICO = R\$\s([0-9\.\,]+)')


    def extract_data(
        self, image_extension: str = 'JPEG'
        ) -> str:
        '''Solved
        '''
        self.pdf_first_page.save(self.pdf_file, image_extension)

        self.ocr_text = pytesseract.image_to_string(
            image=Image.open(self.pdf_file))

        self.nfes_data = re.findall(
            pattern=self.nfes_sp_pattern, string=self.ocr_text)[0]

        return self.ocr_text


    def compose_nfes_data(self) -> None:
        '''Solved
        '''
        sp_im = self.nfes_data[7].replace('.', '').replace('-', '')
        nfes_code = self.nfes_data[5].replace('-', '')

        nfes_id = self.nfes_data[0][-3:]

        key_values = {
            'InscricaoPrestador': sp_im,
            'NumeroNFe': f'0000{nfes_id}',
            'CodigoVerificacao': nfes_code
        }

        nfes_key = SubElement(self.xml, 'ChaveNFe')

        for tag in key_values.items():
            SubElement(nfes_key, tag[0]).text = tag[1]

        nfes_date_str = self.nfes_data[1].split('/')
        nfes_time_str = self.nfes_data[2].split(':')

        nfes_date = [int(string) for string in nfes_date_str]
        nfes_time = [int(string) for string in nfes_time_str]

        nfes_date_time = datetime(
            year=nfes_date[2], month= nfes_date[1], day=nfes_date[0],
            hour=nfes_time[0], minute=nfes_time[1], second=nfes_time[2])

        SubElement(
            self.xml, 'DataEmissaoNFe').text = nfes_date_time.isoformat()

        SubElement(
            self.xml, 'DataFatoGeradorNFe').text = nfes_date_time.isoformat()


    def compose_service_provider_data(self) -> None:
        '''Solved
        '''
        sp_city = self.nfes_data[15]

        if 'SA0' in sp_city:
            sp_city = sp_city.replace('SA0', 'São')

        address = {
            'TipoLogradouro': self.nfes_data[9],
            'Logradouro': self.nfes_data[10],
            'NumeroEndereco': self.nfes_data[11],
            'ComplementoEndereco': self.nfes_data[12],
            'Bairro': self.nfes_data[13],
            'Cidade': sp_city,
            'UF': self.nfes_data[16],
            'CEP': self.nfes_data[14]
        }

        sp_id = SubElement(self.xml, 'CPFCNPJPrestador')
        SubElement(sp_id, 'CNPJ').text = self.nfes_data[6]

        SubElement(self.xml, 'RazaoSocialPrestador').text = self.nfes_data[8]

        sp_address = SubElement(self.xml, 'EnderecoPrestador')

        for tag in address.items():
            SubElement(sp_address, tag[0]).text = tag[1]

        SubElement(self.xml, 'EmailPrestador').text = None


    def compose_taker_data(self) -> None:
        '''Solved
        '''

        address = {
            'TipoLogradouro': 'RUA',
            'Logradouro': self.nfes_data[20] + ' ' + self.nfes_data[21],
            'NumeroEndereco': self.nfes_data[22],
            'ComplementoEndereco': self.nfes_data[23],
            'Bairro': self.nfes_data[24],
            'Cidade': self.nfes_data[26],
            'UF': self.nfes_data[27],
            'CEP': self.nfes_data[25]
        }

        sp_id = SubElement(self.xml, 'CPFCNPJTomador')
        SubElement(sp_id, 'CNPJ').text = self.nfes_data[18]

        SubElement(self.xml, 'RazaoSocialTomador').text = self.nfes_data[17]

        sp_address = SubElement(self.xml, 'EnderecoTomador')

        for tag in address.items():
            SubElement(sp_address, tag[0]).text = tag[1]

        SubElement(self.xml, 'EmailTomador').text = None


    def compose_service_data(self) -> str:
        '''Solved
        '''
        invoice_price = self.nfes_data[31].replace('.', '').replace(',', '.')
        SubElement(self.xml, 'ValorServicos').text = invoice_price

        details = self.nfes_data[29]

        replacements = [
            {'old': '\n', 'new': ' '},
            {'old': 'depésito', 'new': 'depósito'},
            {'old': 'Agéncia', 'new': 'Agência'},
            {'old': 'é', 'new': 'é'},
            {'old': 'Razdo', 'new': 'Razão'}
        ]

        for ch_str in replacements:
            details = details.replace(ch_str['old'], ch_str['new'])

        SubElement(self.xml, 'Discriminacao').text = details


    def log(
        self, file_name: str, file_extension: str = 'xml'
        ) -> None:
        '''Solved
        '''
        file_name = f'{file_name}.{file_extension}'

        ElementTree(self.xml).write(
            file_or_filename=file_name, encoding='utf-8', xml_declaration=True)
