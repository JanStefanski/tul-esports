import server
from waitress import serve

serve(server.app, url_scheme='https', unix_socket="/tmp/nginx.socket", unix_socket_perms="777",
      trusted_proxy="localhost",
      trusted_proxy_headers="x-forwarded-for x-forwarded-host x-forwarded-proto x-forwarded-port")
