from server import server
from waitress import serve
import logging


if __name__ == '__main__':
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)
    serve(server, port=5000, threads=30)
    
        
