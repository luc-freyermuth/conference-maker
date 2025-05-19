from server import server
from config import is_dev_mode
import webview 

if __name__ == '__main__':
    window = webview.create_window('FoCon | Créateur de conférences', server, http_port=5000)
    webview.start(debug=is_dev_mode())
    
        
