'''Solved
'''

from nfes.nota_fiscal_sp import NotaFiscalSP

nfes = NotaFiscalSP('file.pdf')
nfes.extract_data()
nfes.compose_nfes_data()
nfes.compose_service_provider_data()
nfes.compose_taker_data()
nfes.compose_service_data()