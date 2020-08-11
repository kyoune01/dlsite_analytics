#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import (
    QCalendarWidget,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QLineEdit,
    QLabel,
    QApplication
)
from PyQt5.QtCore import QDate


class sabCalendarFrame(QWidget):
    def __init__(self, indexNum, parent=None):
        super().__init__()
        self.result = ""
        self.indexNum = indexNum
        self.parent = parent

        # カレンダーウィジェットの作成
        self.cal = QCalendarWidget(self)
        self.cal.setGridVisible(True)
        self.cal.move(20, 20)
        # 日付がクリックされたら__close関数を呼び出す
        self.cal.clicked[QDate].connect(self.__close)
        self.setGeometry(300, 300, 320, 250)
        self.setWindowTitle('Calendar')

    def __close(self, date=None):
        self.parent.setDateText(date.toString(), self.indexNum)
        self.close()


class viewFrame(QWidget):
    def __init__(self, inpTexts, windowTitle):
        super().__init__()
        self.itemList = []
        self.resultList = []

        self.WINDOWTITLE = windowTitle
        self.INPTEXTS = inpTexts
        self.WIDTH = 500
        self.HEIGHT = len(self.INPTEXTS) * 50
        self.__initUI()

    def __initUI(self):
        # window
        self.setWindowTitle(self.WINDOWTITLE)
        self.setGeometry(300, 300, self.WIDTH, self.HEIGHT)
        self.setMinimumHeight(self.HEIGHT)
        self.setMinimumWidth(self.WIDTH)
        self.setMaximumHeight(self.HEIGHT)
        self.setMaximumWidth(self.WIDTH)

        # generate inputArea
        inpArea = QGridLayout()
        for index, inpText in enumerate(self.INPTEXTS):
            if inpText["type"] == "dirPath":
                inpArea.addLayout(
                    self.__inpLabel(inpText["text"]), index, 0
                )
                inpArea.addLayout(
                    self.__dirPath(), index, 1
                )
            elif inpText["type"] == "lineDate":
                inpArea.addLayout(self.__inpLabel(
                    inpText["text"]), index, 0
                )
                inpArea.addLayout(
                    self.__lineDate(), index, 1
                )
            elif inpText["type"] == "spanDate":
                inpArea.addLayout(self.__inpLabel(
                    inpText["text"]), index, 0
                )
                inpArea.addLayout(
                    self.__spanDate(), index, 1
                )
            elif inpText["type"] == "lineText":
                inpArea.addLayout(self.__inpLabel(
                    inpText["text"]), index, 0
                )
                inpArea.addLayout(
                    self.__inpLineTextNoneBtn(), index, 1
                )
            elif inpText["type"] == "Checkbox":
                #
                # 未実装
                #
                inpArea.addLayout(
                    self.__inpLabel(inpText["text"]), index, 0
                )
                inpArea.addLayout(
                    self.__checkBox(), index, 1
                )

        # genelate SubmitArea
        btnArea = QHBoxLayout()
        btnItem = QPushButton("submit")
        btnItem.clicked.connect(self.__clickSubmitBtn)
        btnArea.addWidget(btnItem)
        btnItem = QPushButton("cancel")
        btnItem.clicked.connect(self.__clickCancelBtn)
        btnArea.addWidget(btnItem)

        # set layout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(inpArea)
        mainLayout.addLayout(btnArea)
        self.setLayout(mainLayout)

    ##
    # type別
    #
    def __dirPath(self):
        dirLayout = QHBoxLayout()
        dirLayout.addLayout(
            self.__inpLineTextExistBtn(self.__setEventBtnToDir)
        )
        return dirLayout

    def __lineDate(self):
        dateLayout = QHBoxLayout()
        dateLayout.addLayout(
            self.__inpLineTextExistBtn(self.__setEventBtnToDate)
        )
        return dateLayout

    def __spanDate(self):
        dateLayout = QHBoxLayout()
        dateLayout.addLayout(
            self.__inpLineTextExistBtn(self.__setEventBtnToDate)
        )
        dateLayout.addLayout(
            self.__inpLabel("～")
        )
        dateLayout.addLayout(
            self.__inpLineTextExistBtn(self.__setEventBtnToDate)
        )
        return dateLayout

    def __checkBox(self):
        inpLayout = QHBoxLayout()
        inpLayout.addLayout(
            self.__inpLabel("yes")
        )
        inpLayout.addLayout(
            self.__inpCheckBox()
        )
        inpLayout.addLayout(
            self.__inpLabel("no")
        )
        inpLayout.addLayout(
            self.__inpCheckBox()
        )
        return inpLayout

    ##
    # BtnClickイベント
    #
    def __setEventBtnToDir(self, inpItem, indexNum):
        dirPath = QFileDialog.getExistingDirectory(
            self,
            'Open Directory',
            os.path.expanduser('~')
        )
        inpItem.setText(dirPath)

    def __setEventBtnToDate(self, inpItem, indexNum):
        self.subWindow = sabCalendarFrame(indexNum, self)
        self.subWindow.show()

    def setDateText(self, text, indexNum):
        date = text.split()
        self.itemList[indexNum].setText(
            "{}-{}-{}".format(date[3], date[1], date[2]))

    ##
    # 共通パーツ
    #
    def __inpLabel(self, text):
        inpLayout = QHBoxLayout()
        inpLayout.addWidget(QLabel(text))
        return inpLayout

    def __inpLineTextExistBtn(self, event):
        inpLayout = QHBoxLayout()
        inpItem = QLineEdit()
        self.itemList.append(inpItem)
        inpLayout.addWidget(inpItem)
        btnItem = QPushButton("...")
        btnItem.clicked.connect(
            lambda: event(inpItem, self.itemList.index(inpItem))
        )
        inpLayout.addWidget(btnItem)
        return inpLayout

    def __inpLineTextNoneBtn(self):
        inpLayout = QHBoxLayout()
        inpItem = QLineEdit()
        self.itemList.append(inpItem)
        inpLayout.addWidget(inpItem)
        return inpLayout

    def __inpCheckBox(self):
        pass

    ##
    # submit処理
    #
    def __clickSubmitBtn(self):
        self.resultList = [item.text() for item in self.itemList]
        self.close()

    def __clickCancelBtn(self):
        self.close()


def viewWindow(inpTexts=[], windowTitle=""):
    if inpTexts == []:
        raise ValueError("catch none arr")
    if windowTitle == "":
        windowTitle = "Qt window"
    app = QApplication(sys.argv)
    w = viewFrame(inpTexts, windowTitle)
    w.show()
    app.exec_()

    if w.resultList == []:
        raise ValueError("result empty")
    else:
        return w.resultList


if __name__ == '__main__':
    viewWindow()
