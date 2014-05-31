import requests
import pyDes
from BeautifulSoup import BeautifulSoup
from xml.etree import ElementTree

url = {
    'keep_alive': 'https://www.unicaja.es/movil/servlet/KeepAliveServlet',
    'main': 'https://www.unicaja.es/movil/servlet/ConnectionServlet',
    'control': 'https://www.unicaja.es/movil/servlet/ControlServlet'
}

class Unicaja:
    def __init__(self, username, password):
        self.__session = requests.Session()
        self.__accounts = {}

        response = self.__session.post(url['keep_alive'])
        key = ElementTree.fromstring(response.text).findall('clave')[0].text

        enc_password = pyDes.des(key, mode=pyDes.CBC, IV='00000000', pad='\0').encrypt(password).encode('hex')
        enc_password = enc_password.upper()

        response = self.__session.post(url['main'], params={ 'tipoPeticion': '1', 
                                                             'menu': 'principal', 
                                                             'usuario': username,
                                                             'password': enc_password,
                                                             'clave': '' })
        self.__dom = BeautifulSoup(response.text)

        response = self.__session.post(url['control'], params={ 'o': 'smcta',
                                                                'p': '01',
                                                                'menu': 'cuentas',
                                                                'titmenu': 'cuentas',
                                                                'opc': '1' })
        self.__dom_accounts = BeautifulSoup(response.text)
        fields = self.__dom_accounts.findAll(id='listaProductos')
        for field in fields:
            s = field.text.split(':')
            account = s[0].replace('Saldo', '').replace('&nbsp; ', '')
            balance = s[1].replace('Dispo', '')
            self.__accounts[account] = {
                'balance': balance,
                'transactions': []
            }

        for account in self.__accounts.keys():
            response = self.__session.post(url['control'], params={ 'o': 'smcta',
                                                                    'p': '02',
                                                                    'menu': 'cuentas',
                                                                    'ppp': account.replace(' ', ''),
                                                                    'claseProd': '11' })
            dom = BeautifulSoup(response.text)
            t = [table.find('tr').text for table in dom.findAll('table')]
            r = [table.find('span').text for table in dom.findAll('table')]
            self.__accounts[account]['transactions'] = zip(t, r)[1:]

    @property
    def username(self):
        return self.__dom.find(id='usuario').getString()

    @property
    def accounts(self):
        return self.__accounts
