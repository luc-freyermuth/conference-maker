from server import server
from config import is_dev_mode
import webview 

if __name__ == '__main__':
    window = webview.create_window('FoCon | Créateur de conférences', 'http://localhost:5000')
    webview.start(debug=is_dev_mode(), server=server, server_args={"port": 5000})
    
        
