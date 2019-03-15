dsn = "http://2947956de96e47b48529ac4525da968:4ab0324f80a24c7f9b5faba8dcf9b8b5@47.92.87.172:9000/2"

from  raven import Client   #导入Client

client = Client(dsn)

try:
    1/0
except ZeroDivisionError:   #捕获错误发送给sentry
    client.captureException()