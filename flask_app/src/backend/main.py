from server import server
from config import is_dev_mode
import webview 

if __name__ == '__main__':
    #server.run(port=5000)
    window = webview.create_window('FoCon | Créateur de conférences', server)
    webview.start(debug=is_dev_mode())
        
