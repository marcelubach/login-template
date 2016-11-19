REM C:\"Program Files (x86)"\Google\google_appengine\dev_appserver.py %1
REM dev_appserver.py --enable_sendmail --port=14080 .\
REM dev_appserver.py --skip_sdk_update_check yes --port 14080 --admin_port 8006 --enable_sendmail C:\code\projects\login-template\login-template-server
dev_appserver.py --skip_sdk_update_check yes --port 19080 --admin_port 8006 --enable_sendmail true .
