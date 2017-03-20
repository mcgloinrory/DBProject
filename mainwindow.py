#!/usr/bin/python

import sys
import pymysql
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
        QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QTextEdit)

# DB Credentials
hostname = 'localhost'
username = 'testuser'
password = 'test'
database = 'starwars'
myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database )

# Query the DB
def doQuery( conn ) :
    cur = conn.cursor()

    cur.execute( "SELECT * FROM characters" )

    return cur.fetchall()

# Main Window
class Window(QWidget):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.grid = QGridLayout()
        self.log = QTextEdit()
        buttonGroup = self.createButtonGroup()
        textboxGroup = self.createTextBoxGroup()
        self.grid.addWidget(buttonGroup, 0, 0)
        self.grid.addWidget(textboxGroup, 1, 0)
        self.setLayout(self.grid)

        self.setWindowTitle("Group Box")
        self.resize(480, 320)

    def createButtonGroup(self):
    	groupBox = QGroupBox("Button button button")

    	button1 = QPushButton("SELECT * FROM characters")
    	button1.clicked.connect(self.handleClick)

    	vbox = QVBoxLayout()
    	vbox.addWidget(button1)
    	vbox.addStretch(1)
    	groupBox.setLayout(vbox)

    	return groupBox

    def createTextBoxGroup(self):
    	groupBox = QGroupBox("Text area")

    	self.log.setReadOnly(True)

    	vbox = QVBoxLayout()
    	vbox.addWidget(self.log)
    	vbox.addStretch(1)
    	groupBox.setLayout(vbox)

    	return groupBox

    def handleClick(self, event):
    	results = doQuery( myConnection )
    	self.log.clear()
    	for name, race, planet, affiliation in results:
    		self.log.append(name + " " + race + " " + planet + " " + affiliation)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())