from rest_framework.exceptions import APIException


class BusinessException(APIException):
    status_code = 400
    default_detail = '业务处理异常'
    default_code = 'business_error'
