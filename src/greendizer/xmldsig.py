# -*- coding: utf-8 -*-

'''
XMLDSig: Sign and Verify XML digital cryptographic signatures.
xmldsig is a minimal implementation of bytestring cryptographic
xml digital signatures

@note: Adapted from Andrew D. Yates' implementation of xmldsig for python 
'''
try:
    import lxml.etree as etree
except ImportError:
    raise ImportError("lxml is required but could not be find.")

import hashlib
import binascii
from StringIO import StringIO
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util.number import long_to_bytes


PTN_SIGNED_INFO_XML = \
'<SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#"><CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments"></CanonicalizationMethod><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></SignatureMethod><Reference URI=""><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></Transform></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></DigestMethod><DigestValue>%(digest_value)s</DigestValue></Reference></SignedInfo>'

PTN_SIGNATURE_XML = \
'<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">%(signed_info_xml)s<SignatureValue>%(signature_value)s</SignatureValue>%(key_info_xml)s</Signature>'

PTN_KEY_INFO_RSA_KEY = \
'<KeyInfo><KeyValue><RSAKeyValue><Modulus>%(modulus)s</Modulus><Exponent>%(exponent)s</Exponent></RSAKeyValue></KeyValue></KeyInfo>'


def b64e(s):
    if type(s) in [int, long]:
        s = long_to_bytes(s)
    return s.encode('base64').replace('\n', '')


def c14n(xml):
    '''
    Applies c14n to the xml input
    @param xml: str
    @return: str
    '''
    tree = etree.parse(StringIO(xml))
    output = StringIO()
    tree.write_c14n(output, exclusive=False, with_comments=True, compression=0)
    output.flush()
    c14nized = output.getvalue().decode('utf-8')
    output.close()
    return c14nized


def sign(xml, private, public):
    '''
    Return xmldsig XML string from xml_string of XML.
    @param xml: str of bytestring xml to sign
    @param private: publicKey Private key
    @param public: publicKey Public key 
    @return str: signed XML byte string
    '''
    xml = xml.encode('utf-8', 'xmlcharrefreplace')
    signed_info_xml = _generate_signed_info(xml)

    signer = PKCS1_v1_5.PKCS115_SigScheme(private)
    signature_value = signer.sign(SHA.new(c14n(signed_info_xml)))

    signature_xml = PTN_SIGNATURE_XML % {
        'signed_info_xml': signed_info_xml,
        'signature_value': binascii.b2a_base64(signature_value)[:-1],
        'key_info_xml': _generate_key_info_xml_rsa(public.key.n, public.key.e)
    }

    position = xml.rfind('</')
    return xml[0:position] + signature_xml + xml[position:]


def _generate_key_info_xml_rsa(modulus, exponent):
    '''
    Return <KeyInfo> xml bytestring using raw public RSA key.
    @param modulus: str of bytes
    @param exponent: str of bytes
    @return str of bytestring xml
    '''
    return PTN_KEY_INFO_RSA_KEY % {'modulus': b64e(modulus),
                                   'exponent': b64e(exponent)}


def _generate_signed_info(xml):
    '''
    Applies c14n and returns <SignedInfo> for bytestring xml.
    @param xml: str of bytestring
    @return: str of <SignedInfo> computed from `xml`
    '''
    return PTN_SIGNED_INFO_XML % {'digest_value': b64e(hashlib.sha1(c14n(xml))
                                                       .digest()) }

