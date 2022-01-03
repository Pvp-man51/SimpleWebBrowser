from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *

import os
import sys


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        qbtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(qbtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("Chrome (Scuffed Edition)")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join("images", "ma-icon-128.png")))
        layout.addWidget(logo)

        layout.addWidget(QLabel("Version 1.0.0.0"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    htmlFinished = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.mHtml = ""

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Fonts/Robot-Medium.ttf", 10))
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # navbar
        navbar = QToolBar("Navigation")
        navbar.setFont(QFont("Fonts/Roboto-Medium.ttf", 10))
        navbar.setIconSize(QSize(16, 16))
        self.addToolBar(navbar)

        back_btn = QAction(QIcon(os.path.join("images", "arrow-180.png")), "Back", self)
        back_btn.setShortcut("Alt+Left")
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navbar.addAction(back_btn)

        forward_btn = QAction(QIcon(os.path.join("images", "arrow-000.png")), "Forward", self)
        forward_btn.setShortcut("Alt+Right")
        forward_btn.setStatusTip("Forward to next page")
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navbar.addAction(forward_btn)

        reload_btn = QAction(QIcon(os.path.join("images", "arrow-circle-315.png")), "Reload", self)
        reload_btn.setShortcut("function5")
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navbar.addAction(reload_btn)

        home_btn = QAction(QIcon(os.path.join("images", "home.png")), "Home", self)
        reload_btn.setShortcut("Ctrl+H")
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        navbar.addSeparator()

        self.httpsicon = QLabel()
        self.httpsicon.setPixmap(QPixmap(os.path.join("images", "lock-nossl.png")))
        navbar.addWidget(self.httpsicon)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        stop_btn = QAction(QIcon(os.path.join("images", "cross-circle.png")), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navbar.addAction(stop_btn)

        file_menu = self.menuBar().addMenu("&File")

        new_tab_action = QAction(QIcon(os.path.join("images", "ui-tab--plus.png")), "New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.setStatusTip("Open a new Tab")
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        open_file_action = QAction(QIcon(os.path.join("images", "disk--arrow.png")), "Open file...", self)
        open_file_action.setStatusTip("Open from file")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join("images", "disk--pencil.png")), "Save Page As...", self)
        save_file_action.setShortcut("Ctrl+S")
        save_file_action.setStatusTip("Save current page to file")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)

        print_action = QAction(QIcon(os.path.join("images", "printer.png")), "Print...", self)
        print_action.setShortcut("Ctrl+P")
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)

        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction(QIcon(os.path.join("images", "question.png")), "About Chrome (Scuffed Edition)", self)
        about_action.setStatusTip("Find out more about Chrome (Scuffed Edition)")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        navigate_help_action = QAction(QIcon(os.path.join("images", "GitHub-Mark-32px.png")),
                                            "Github", self)
        navigate_help_action.setStatusTip("Go to Chrome (Scuffed Edition)'s Github page")
        navigate_help_action.triggered.connect(self.navigate_github)
        help_menu.addAction(navigate_help_action)

        self.add_new_tab(QUrl("http://google.com"), "Homepage")

        self.showMaximized()

        self.setWindowTitle("Chrome (Scuffed Edition)")
        self.setFont(QFont("Fonts/Roboto-Medium.ttf", 10))

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl("http://google.com")

        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - Chrome (Scuffed Edition)" % title)

    def navigate_github(self):
        self.tabs.currentWidget().setUrl(QUrl("https://github.com/Pvp-man51"))

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "Hypertext Markup Language (*.htm *.html);;"
                                                  "Portable Document Format (*.pdf);;"
                                                  "Text Document (*.txt);;"
                                                  "All files (*.*)")
        if filename:
            with open(filename, 'r') as f:
                html = f.read()

            self.tabs.currentWidget().setHtml(html)
            self.url_bar.setText("File")

    def callback(self, html):
        self.mHtml = html
        self.htmlFinished.emit()

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", f"{self.tabs.currentWidget().url()}.html",
                                                  "Hypertext Markup Language (*.htm *.html);;"
                                                  "Portable Document Format (*.pdf);;"
                                                  "Text Document (*.txt);;"
                                                  "All files (*.*)")
        if filename:
            self.tabs.currentWidget().page().toHtml(self.callback)
            loop = QEventLoop()
            self.htmlFinished.connect(loop.quit)
            loop.exec_()
            with open(filename, 'w') as f:
                f.write(self.mHtml)

    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.handle_paint_request)
        dlg.exec_()

    def handle_paint_request(self, printer):
        painter = QPainter(printer)
        painter.setViewport(self.tabs.currentWidget().rect())
        painter.setWindow(self.tabs.currentWidget().rect())
        self.tabs.currentWidget().render(painter)
        painter.end()

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://google.com"))

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())

        if q.scheme() == "":
            q.setScheme("http")

        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return

        if q.scheme() == "https":
            # Secure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join("images", "lock-ssl.png")))

        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join("images", "lock-nossl.png")))

        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)


# Creates the Window
app = QApplication(sys.argv)
app.setWindowIcon(QIcon(os.path.join("images", "icon.png")))
app.setApplicationName("Chrome (Scuffed Edition)")
app.setOrganizationName("Pvp-man")

window = MainWindow()

app.exec_()
