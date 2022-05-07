# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "10.16.127.6"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Get was here!")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>MuleBot Test Web Server!.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
    def do_POST(self):
        print("Post was here")
        '''Reads post request body'''
        self._set_headers()
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        self.wfile.write("received post request:<br>{}".format(post_body))

    def do_PUT(self):
        print("Put was here")
        self.do_POST()

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")