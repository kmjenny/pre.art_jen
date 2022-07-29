# 전화번호 인증 부분
import hashlib
import hmac
import base64

# 전화번호 인증
def make_signature(timestamp):
    access_key = 'RBRMXDItYtF7hcR3kurm'
    secret_key = '0JGYh7u8TKPx6XAwjAdWHpXx5aO2vKlKdUtKOBWq'
    secret_key = bytes(secret_key, 'UTF-8')

    uri = "/sms/v2/services/ncp:sms:kr:289537147905:pre_art/messages"

    message = "POST" + " " + uri + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return signingKey
