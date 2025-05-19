from server import server
from config import is_dev_mode
import webview 

def runserver():
    server.run(port=5000)

if __name__ == '__main__':
    window = webview.create_window('FoCon | Créateur de conférences', 'http://localhost:5000')
    webview.start(runserver,  debug=is_dev_mode())
    
        
