from server import server
from waitress import serve


if __name__ == '__main__':
    serve(server, port=5000)
    
        
