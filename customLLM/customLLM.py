import g4f
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


import logging



class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        logging.basicConfig(filename='app.log', level=logging.INFO)
        logging.info('New LLM call')
        logging.info('-----------------------------------')

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            prompt = data.get("message")

            response = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                )

            concatenated_message = ""

            for message in response:
                concatenated_message = concatenated_message + message

            out = {"response": concatenated_message}
            logging.info(out)
            logging.info('-----------------------------------')
            logging.info('')
            logging.info('')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(out).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode())

if __name__ == '__main__':
    httpd = HTTPServer(('0.0.0.0', 5000), SimpleHTTPRequestHandler)
    httpd.serve_forever()
