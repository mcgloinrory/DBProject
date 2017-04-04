#!/usr/bin/python

import sys
import time
import pymysql
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
		QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout,
		QLineEdit, QDialog, QLabel)
from yahoo_finance import Share

# DB Credentials
hostname = 'localhost'
username = 'testuser'
password = 'test'
database = 'mydb'
myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database, autocommit=True )

# Query the DB
def doQuery(conn, query):
	cur = conn.cursor()
	cur.execute(query)
	return cur.fetchall()

# Get stocks that exist in the DB
def getStocks():
	shares = []
	for stock in doQuery(myConnection, 'SELECT stock FROM Stocks'):
		shares.append(stock[0])
	return shares

# Get most recent date historical_data was refreshed
def getRecentDate():
	return str(doQuery(myConnection, 'SELECT most_recent_data()')[0][0])

# Window to show the results of info check
class ResultWindow(QDialog):

	def __init__(self, result, parent=None):
		super(ResultWindow, self).__init__(parent)

		self.grid = QGridLayout()
		self.grid.addWidget(QLabel("Company Info"), 0, 0)
		self.log = QTextEdit()
		self.log.setText(str(result))
		self.log.setReadOnly(True)
		self.grid.addWidget(self.log, 1, 0)
		self.button = QPushButton("Return To Homepage")
		self.button.clicked.connect(self.handleClick)
		self.grid.addWidget(self.button)
		self.setLayout(self.grid)

	def handleClick(self, event):
		self.hide()
		return


# Window for checking Stock Info
class InfoWindow(QDialog):

	def __init__(self, parent=None):
		super(InfoWindow, self).__init__(parent)
		self.grid = QGridLayout()
		self.grid.addWidget(QLabel("Enter Ticker:"), 0, 0)
		self.textfield = QTextEdit()
		self.grid.addWidget(self.textfield, 1, 0)
		enterbutton = QPushButton("Enter")
		enterbutton.clicked.connect(self.handleClick)
		self.grid.addWidget(enterbutton)
		self.setLayout(self.grid)
		self.resize(200, 100)
		self.show()

	def handleClick(self, event):
		ticker = self.textfield.toPlainText()
		result = doQuery(myConnection, "SELECT s.name FROM Stocks s WHERE s.stock = '" + ticker + "'")
		if result:
			self.resultDialog(result[0][0])
		else:
			self.resultDialog("The ticker entered did not match a known company")
		return

	def resultDialog(self, result):
		dialog = ResultWindow(result, self)
		dialog.show()
		self.hide()

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
		self.infowindow = InfoWindow()
		self.infowindow.show()
		return self.infowindow

	def handleBuy(self, event):
		return

	def handleSell(self, event):
		return

	def handleRefresh(self, event):
		lastDate = getRecentDate()
		shares = getStocks()
		for s in shares:
			share = Share(s)
			try:
				for stock in share.get_historical(lastDate, time.strftime("%Y-%m-%d")):
					doQuery(myConnection, "INSERT INTO `Historical_Data` (`date`, `stock`, `adj_closed`) VALUES ('" + stock['Date'] + "', '" + stock['Symbol'] + "', '" + stock['Adj_Close'] + "')")
			except:
				print('Error encountered')
		return


if __name__ == '__main__':

	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec_())