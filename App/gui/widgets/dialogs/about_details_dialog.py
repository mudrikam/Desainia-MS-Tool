from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                            QWidget, QHBoxLayout, QTextBrowser, QApplication)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QPalette, QColor
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

class AboutDetailsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Details")
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add network manager for loading remote images
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._handle_network_response)
        
        # Create text browser with improved styling
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.anchorClicked.connect(self.handle_link)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                border: 1px solid palette(mid);
                border-radius: 6px;
                padding: 20px;
                font-size: 12px;
            }
            QScrollBar:vertical {
                border: none;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                border-radius: 5px;
            }
        """)
        
        # Load README content
        app = QApplication.instance()
        readme_path = app.BASE_DIR.get_path('README.md')
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Handle badge markdown with improved SVG handling
                import re
                def badge_replacement(match):
                    alt_text = match.group(1)
                    image_url = match.group(2)
                    link_url = match.group(3)
                    
                    # Convert SVG shields.io URLs to PNG
                    if 'shields.io' in image_url and image_url.endswith('.svg'):
                        image_url = image_url.replace('.svg', '.png')
                    
                    request = QNetworkRequest(QUrl(image_url))
                    request.setAttribute(QNetworkRequest.Attribute.CacheLoadControlAttribute, 
                                      QNetworkRequest.CacheLoadControl.PreferCache)
                    self.network_manager.get(request)
                    
                    return f'''<a href="{link_url}"><img src="{image_url}" 
                        alt="{alt_text}" height="20" style="margin: 4px 2px;"></a>'''
                
                # Process badges first
                content = re.sub(r'\[\!\[(.*?)\]\((.*?)\)\]\((.*?)\)', badge_replacement, content)
                
                # Handle other markdown links
                def link_replacement(match):
                    text = match.group(1)
                    url = match.group(2)
                    
                    # Handle relative paths and avoid processing already processed badges
                    if url.startswith('./'):
                        url = f"https://github.com/mudrikam/Desainia-MS-Tool/blob/main/{url[2:]}"
                    elif url.endswith('.svg'):
                        return match.group(0)  # Skip SVG links that weren't badges
                    
                    return f'<a href="{url}">{text}</a>'
                
                content = re.sub(r'\[(.*?)\]\((.*?)\)', link_replacement, content)
                
                # Handle lists
                lines = content.split('\n')
                in_list = False
                processed_lines = []
                
                for line in lines:
                    # Skip lines that are already HTML
                    if re.match(r'<[^>]+>', line.strip()):
                        processed_lines.append(line)
                        continue
                        
                    if line.strip().startswith('- '):
                        if not in_list:
                            processed_lines.append('<ul>')
                            in_list = True
                        processed_lines.append(f'<li>{line.strip()[2:]}</li>')
                    else:
                        if in_list:
                            processed_lines.append('</ul>')
                            in_list = False
                        processed_lines.append(line)
                
                if in_list:
                    processed_lines.append('</ul>')
                
                content = '\n'.join(processed_lines)
                
                # Basic Markdown to HTML conversion
                content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
                content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
                content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
                
                # Handle emphasis/bold outside lists
                content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
                content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
                
                # Handle blockquotes
                lines = content.split('\n')
                processed_lines = []
                for line in lines:
                    if line.startswith('> '):
                        processed_lines.append(f'<blockquote>{line[2:]}</blockquote>')
                    else:
                        processed_lines.append(line)
                content = '\n'.join(processed_lines)
                
                # Handle paragraphs properly - exclude HTML tags
                paragraphs = content.split('\n\n')
                content = '\n'.join(
                    p.strip() if any(p.strip().startswith(tag) for tag in 
                        ['<h1>', '<h2>', '<h3>', '<table>', '<blockquote>', '<p>']) 
                    else f'<p>{p.strip()}</p>' 
                    for p in paragraphs if p.strip()
                )
                
                # Enhanced CSS styling
                html = f"""
                <style>
                    body {{ 
                        font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;
                        font-size: 12px;
                        line-height: 1.6;
                        max-width: 850px;
                        margin: 0 auto;
                    }}
                    h1 {{ 
                        font-size: 24px; 
                        margin: 24px 0 16px 0;
                        padding-bottom: 0.3em; 
                        border-bottom: 1px solid palette(mid);
                        font-weight: 600;
                        line-height: 1.25;
                    }}
                    h2 {{ 
                        font-size: 20px; 
                        margin: 24px 0 16px 0;
                        padding-bottom: 0.3em; 
                        border-bottom: 1px solid palette(mid);
                        font-weight: 600;
                        line-height: 1.25;
                    }}
                    h3 {{ 
                        font-size: 16px; 
                        margin: 24px 0 16px 0;
                        font-weight: 600;
                        line-height: 1.25;
                    }}
                    p {{ 
                        line-height: 1.6; 
                        margin: 1em 0;
                        font-size: 12px;
                    }}
                    code {{ 
                        padding: 0.2em 0.4em; 
                        border-radius: 3px; 
                        font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;
                        font-size: 11px;
                    }}
                    table {{ 
                        border-collapse: collapse; 
                        width: 100%;
                        margin: 1em 0; 
                        font-size: 12px;
                    }}
                    td, th {{ 
                        border: 1px solid palette(mid);
                        padding: 8px 12px;
                    }}
                    blockquote {{ 
                        border-left: 0.25em solid palette(mid);
                        border-radius: 6px;
                        margin: 1.5em 0;
                        padding: 1em 1.2em;
                        font-size: 12px;
                        line-height: 1.6;
                    }}
                    ul {{
                        margin: 0.8em 0;
                        padding-left: 2em;
                    }}
                    li {{
                        margin: 0.3em 0;
                        font-size: 12px;
                        line-height: 1.6;
                    }}
                    strong {{
                        font-weight: 600;
                    }}
                    em {{
                        font-style: italic;
                    }}
                    img {{ 
                        vertical-align: middle;
                        max-width: 100%;
                    }}
                    a {{ 
                        text-decoration: none;
                        transition: color 0.2s ease;
                    }}
                    a:hover {{ 
                        text-decoration: underline;
                    }}
                </style>
                {content}
                """
                self.text_browser.setHtml(html)
        except Exception as e:
            self.text_browser.setPlainText(f"Error loading README: {str(e)}")
        
        layout.addWidget(self.text_browser)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def handle_link(self, url):
        """Handle clicked links by opening in default browser"""
        QDesktopServices.openUrl(url)
        return True
    
    def _handle_network_response(self, reply):
        """Handle network responses for image loading"""
        if reply.error() == QNetworkReply.NetworkError.NoError:
            url = reply.url().toString()
            self.text_browser.document().addResource(
                4,  # QTextDocument.ImageResource
                QUrl(url),
                reply.readAll()
            )
            self.text_browser.viewport().update()
