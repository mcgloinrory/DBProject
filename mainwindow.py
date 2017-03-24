#!/usr/bin/python

import sys
import pymysql
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
		QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout)
from yahoo_finance import Share

# DB Credentials
hostname = 'localhost'
username = 'testuser'
password = 'test'
database = 'mydb'
myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database )

# Query the DB
def doQuery(conn, query) :
	cur = conn.cursor()
	cur.execute(query)
	return cur.fetchall()

# Main Window
class Window(QWidget):

	def __init__(self, parent=None):
		super(Window, self).__init__(parent)

		self.grid = QGridLayout()
		self.log = QTextEdit()
		self.grid.addWidget(self.createButtonGroup(), 0, 0)
		self.grid.addWidget(self.createTextBoxGroup(), 1, 0)
		self.grid.addWidget(self.createRefreshButton(), 2, 0)
		self.setLayout(self.grid)

		self.setWindowTitle("Portfolio Manager")
		self.resize(360, 320)

	def createButtonGroup(self):
		groupBox = QGroupBox()

		infobutton = QPushButton("Stock Info")
		infobutton.clicked.connect(self.handleInfo)
		buybutton = QPushButton("Buy Stock")
		buybutton.clicked.connect(self.handleBuy)
		sellbutton = QPushButton("Sell Stock")
		sellbutton.clicked.connect(self.handleSell)

		hbox = QHBoxLayout()
		hbox.addWidget(infobutton)
		hbox.addWidget(buybutton)
		hbox.addWidget(sellbutton)
		hbox.addStretch(1)
		groupBox.setLayout(hbox)

		return groupBox

	def createTextBoxGroup(self):
		groupBox = QGroupBox()

		self.log.setReadOnly(True)

		vbox = QVBoxLayout()
		vbox.addWidget(self.log)
		vbox.addStretch(1)
		groupBox.setLayout(vbox)

		return groupBox

	def createRefreshButton(self):
		button = QPushButton("Data Refresh")
		button.clicked.connect(self.handleRefresh)
		return button

	def handleInfo(self, event):
		return

	def handleBuy(self, event):
		return

	def handleSell(self, event):
		return

	def handleRefresh(self, event):
		share = Share('YHOO')
		self.log.clear()
		for stock in share.get_historical('2015-05-10', '2015-05-15'):
			self.log.append(stock['Symbol'] + ": " + stock['Adj_Close'])
		return


if __name__ == '__main__':

	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec_())