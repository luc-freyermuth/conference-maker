from server import server
import webview

if __name__ == '__main__':
    #server.run(port=5000)
    window = webview.create_window('My first pywebview application', server)
    webview.start()
        
