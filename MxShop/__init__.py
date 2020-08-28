import pymysql
# pymysql.version_info = (1, 4, 13, "final", 0)  # 更改版本的信息,对于要求为14而是为10的解决方法
pymysql.install_as_MySQLdb()