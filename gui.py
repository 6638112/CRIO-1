import os
import sys

from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QVBoxLayout,
                             QLabel, QMainWindow, QStatusBar, QToolBar,
                             QAction, QLineEdit, QFileDialog, QApplication)


class Answers:
    def __init__(self, query):
        self.query = query
        self.answer_urls = []
        self.cur_ans_idx = -1
        self.generate_answer_links()
        self.default = 'https://www.stackoverflow.com'

    def generate_answer_links(self):
        """
        Returns a list of StackOverflow answer URLs.
        :param query: Question entered by the user.
        :return: List
        """
        ##################################
        # Bhosdike ye tujhe karna h
        # use self.query to generate URLs
        # I have stored few urls just so you can test the GUI
        urls = [
            'https://stackoverflow.com/a/45013767/7183250',
            'https://stackoverflow.com/a/47990/7183250',
            'https://stackoverflow.com/a/109045/7183250'
        ]
        ##################################
        self.answer_urls.extend(urls)
        return self.answer_urls

    def get_next(self):
        self.cur_ans_idx += 1
        if self.cur_ans_idx == len(self.answer_urls):
            self.cur_ans_idx = 0
        try:
            return self.answer_urls[self.cur_ans_idx]
        except IndexError:
            return self.default

    def get_prev(self):
        self.cur_ans_idx -= 1
        if self.cur_ans_idx < 0:
            self.cur_ans_idx = 0
        try:
            return self.answer_urls[self.cur_ans_idx]
        except IndexError:
            return self.default


class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("CRIO")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('images', 'ma-icon-128.png')))
        layout.addWidget(logo)

        layout.addWidget(QLabel("Copyright 2019 CRIO"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.stackoverflow.com"))

        self.browser.urlChanged.connect(self.update_urlbar)
        self.browser.loadFinished.connect(self.update_title)

        self.setCentralWidget(self.browser)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        #####################################################
        navtb2 = QToolBar()
        navtb2.setIconSize(QSize(16, 16))
        navtb2.setFixedHeight(50)
        navtb2.setIconSize(QSize(60, 60))

        self.query_bar = QLineEdit(self)
        self.query_bar.setFixedHeight(45)
        f = self.query_bar.font()
        f.setPointSize(20)  # sets the size to 27
        self.query_bar.setFont(f)
        self.query_bar.setPlaceholderText("Powered by IBM Cloud...")
        self.query_bar.returnPressed.connect(self.process_query)
        navtb2.addWidget(self.query_bar)

        self.back_btn = QAction(QIcon(os.path.join('images', 'arrow-180.png')), "Previous Answer", self)
        self.back_btn.setStatusTip("Back to previous page")
        self.back_btn.triggered.connect(self.prev_answer)
        self.back_btn.setDisabled(True)
        navtb2.addAction(self.back_btn)

        self.next_btn = QAction(QIcon(os.path.join('images', 'arrow-000.png')), "Next Answer", self)
        self.next_btn.setStatusTip("Forward to next page")
        self.next_btn.triggered.connect(self.next_answer)
        self.next_btn.setDisabled(True)
        navtb2.addAction(self.next_btn)

        self.addToolBar(navtb2)
        self.addToolBarBreak()
        #####################################################

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)

        reload_btn = QAction(QIcon(os.path.join('images', 'arrow-circle-315.png')), "Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(self.browser.reload)
        navtb.addAction(reload_btn)

        home_btn = QAction(QIcon(os.path.join('images', 'home.png')), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        self.httpsicon = QLabel()  # Yes, really!
        self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-nossl.png')))
        navtb.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(QIcon(os.path.join('images', 'cross-circle.png')), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(self.browser.stop)
        navtb.addAction(stop_btn)

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)

        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction(QIcon(os.path.join('images', 'disk--arrow.png')), "Open file...", self)
        open_file_action.setStatusTip("Open from file")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Save Page As...", self)
        save_file_action.setStatusTip("Save current page to file")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)

        print_action = QAction(QIcon(os.path.join('images', 'printer.png')), "Print...", self)
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)

        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction(QIcon(os.path.join('images', 'question.png')), "About CRIO", self)
        about_action.setStatusTip("Find out more about CRIO")  # Hungry!
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        navigate_mozarella_action = QAction(QIcon(os.path.join('images', 'lifebuoy.png')), "CRIO Homepage", self)
        navigate_mozarella_action.setStatusTip("Go to CRIO Homepage")
        navigate_mozarella_action.triggered.connect(self.navigate_mozarella)
        help_menu.addAction(navigate_mozarella_action)

        self.show()

        self.setWindowIcon(QIcon(os.path.join('images', 'ma-icon-64.png')))

    def update_title(self):
        title = self.browser.page().title()
        self.setWindowTitle("%s - CRIO" % title)

    def navigate_mozarella(self):
        self.browser.setUrl(QUrl("https://github.com/fivecube/CRIO"))

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "Hypertext Markup Language (*.htm *.html);;"
                                                  "All files (*.*)")

        if filename:
            with open(filename, 'r') as f:
                html = f.read()

            self.browser.setHtml(html)
            self.urlbar.setText(filename)

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", "",
                                                  "Hypertext Markup Language (*.htm *html);;"
                                                  "All files (*.*)")

        if filename:
            html = self.browser.page().toHtml()
            with open(filename, 'w') as f:
                f.write(html)

    def print_page(self):
        dlg = QPrintPreviewDialog()
        dlg.paintRequested.connect(self.browser.print_)
        dlg.exec_()

    def navigate_home(self):
        self.browser.setUrl(QUrl("http://www.stackoverflow.com"))

    def navigate_to_url(self):  # Does not receive the Url
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.browser.setUrl(q)

    def update_urlbar(self, q):

        if q.scheme() == 'https':
            # Secure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-ssl.png')))
        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-nossl.png')))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def process_query(self):
        q = self.query_bar.text().strip()
        if q.startswith('http:') or q.startswith('https:'):
            self.browser.setUrl(QUrl(q))
        else:
            self.answers = Answers(q)
            self.next_btn.setDisabled(False)
            self.back_btn.setDisabled(False)
            self.next_answer()

    def next_answer(self):
        ans = self.answers.get_next()
        self.browser.setUrl(QUrl(ans))

    def prev_answer(self):
        ans = self.answers.get_prev()
        self.browser.setUrl(QUrl(ans))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("CRIO")
    app.setOrganizationName("CRIO")
    app.setOrganizationDomain("https://github.com/fivecube/CRIO")

    window = MainWindow()

    app.exec_()