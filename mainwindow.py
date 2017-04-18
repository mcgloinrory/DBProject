#!/usr/bin/python

import sys
import time
import datetime


import pymysql
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
							 QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout,
							 QLineEdit, QDialog, QLabel, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.uic.properties import QtCore, QtGui

from yahoo_finance import Share

# DB Credentials
hostname = 'localhost'
username = 'root'
password = 'homesweethome'
database = 'mydb'
myConnection = pymysql.connect(host=hostname, user=username, passwd=password, db=database, autocommit=True)


# Query the DB
def doQuery(conn, query):
	cur = conn.cursor()
	cur.execute(query)
	return cur.fetchall()


# Get stocks that exist in the DB
def getStocks():
	shares = []
	for stock in doQuery(myConnection, 'SELECT * FROM Portfolio'):
		shares.append(stock[1])
	return shares


# Get most recent date historical_data was refreshed
def getRecentDate():
	return str(doQuery(myConnection, 'SELECT most_recent_data()')[0][0])

# Failure result for logging in
class LoginResultWindow(QDialog):
	def __init__(self, result, parent=None):
		super(LoginResultWindow, self).__init__(parent)

		self.grid = QGridLayout()
		self.grid.addWidget(QLabel("User ID was not found. Would you like to make this id?"), 0, 0)
		self.tryagainbutton = QPushButton("Try Again")
		self.tryagainbutton.clicked.connect(self.handleTryAgain(result))
		self.exitbutton = QPushButton("Exit")
		self.exitbutton.clicked.connect(self.handleExit)
		self.groupBox = QGroupBox()
		hbox = QHBoxLayout()
		hbox.addWidget(self.tryagainbutton)
		hbox.addWidget(self.exitbutton)
		hbox.addStretch(1)
		self.groupBox.setLayout(hbox)
		self.grid.addWidget(self.groupBox, 1, 0)
		self.setLayout(self.grid)

	def handleTryAgain(self, event):
		self.loginwindow = LoginWindow(self)
		self.loginwindow.show()
		self.hide()
		return

	def handleExit(self, event):
		self.hide()
		return




# Login prompt for user_id
class LoginWindow(QDialog):
	def __init__(self, result, parent=None):
		super(LoginWindow, self).__init__(parent)

		self.grid = QGridLayout()
		self.grid.addWidget(QLabel("Please Enter Your User Id"), 0, 0)
		self.field = QTextEdit()
		self.grid.addWidget(self.field)
		self.confirmbutton = QPushButton("Confirm")
		self.confirmbutton.clicked.connect(self.handleClick)
		self.grid.addWidget(self.confirmbutton)
		self.setLayout(self.grid)


	def handleClick(self, event):
		id = self.field.toPlainText()

		if doQuery(myConnection, "SELECT * FROM Users u WHERE u.user_id = '" + id + "'"):
			global userId
			userId = id
			self.hide()
			window.show()
		else:
			self.resultWindow = LoginResultWindow(self)
			self.resultWindow.show()
			self.hide()
		return



# Window to show the results of info check
class InfoResultWindow(QDialog):
	def __init__(self, result, parent=None):
		super(InfoResultWindow, self).__init__(parent)

		self.grid = QGridLayout()
		self.grid.addWidget(QLabel("Company Info"), 0, 0)
		self.log = QTextEdit()
		s = Share(result)
		self.log.setText(str(s.get_name()) +  "\n" + "Market Cap: " + str(s.get_market_cap())
		+ "\n" + "Volume: " + str(s.get_volume())
		+ "\n" + "Current Price: " + str(s.get_price()))



		self.log.setReadOnly(True)
		self.grid.addWidget(self.log, 1, 0)
		self.button = QPushButton("Return To Homepage")
		self.button.clicked.connect(self.handleClick)
		self.button2 = QPushButton("Try Again")
		self.button2.clicked.connect(self.tryClick)
		self.grid.addWidget(self.button)
		self.grid.addWidget(self.button2)
		self.setLayout(self.grid)


	def handleClick(self, event):
		self.hide()
		return

	# button to go back to input window if needed (i.e. a typo is made by user)
	def tryClick(self, event):
		self.hide()
		self.infowindow = InfoWindow()
		self.infowindow.show()
		return self.infowindow



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
		result = doQuery(myConnection, "SELECT stock FROM Stocks s WHERE s.stock = '" + ticker + "'")
		if result:
			self.resultDialog(result[0][0])
		else:
			self.resultDialog("The ticker entered did not match a known company")

		return

	def resultDialog(self, result):
		dialog = InfoResultWindow(result, self)
		dialog.show()
		self.hide()

# Window to show results of buying stock
class BuyResultWindow(QDialog):
	def __init__(self, result, parent = None):
		super(BuyResultWindow, self).__init__(parent)
		self.grid = QGridLayout()
		self.grid.addWidget(QLabel("Stock Purchases"), 0, 0)
		self.log = QTextEdit()
		self.log.setText(str(result))
		self.log.setReadOnly(True)
		self.grid.addWidget(self.log, 1, 0)
		self.button = QPushButton("Return To Homepage")
		self.button.clicked.connect(self.handleClick)
		self.button2 = QPushButton("Try Again")
		self.button2.clicked.connect(self.tryClick)
		self.grid.addWidget(self.button)
		self.grid.addWidget(self.button2)
		self.setLayout(self.grid)

	def handleClick(self, event):
		self.hide()
		return

	# button to go back to input window if needed (i.e. a typo is made by user)
	def tryClick(self, event):
		self.hide()
		self.buywindow = BuyWindow()
		self.buywindow.show()
		return self.buywindow

# Window for buying a stock
class BuyWindow(QDialog):
	def __init__(self, parent=None):
		super(BuyWindow, self).__init__(parent)
		self.grid = QGridLayout()
		cur_balance = doQuery(myConnection, "SELECT current_balance FROM users WHERE user_id = " + userId)
		cur_balance = str(cur_balance[0][0])
		self.log = QLineEdit()
		self.log.setText("Current Balance: '" + cur_balance + "'")
		self.log.setReadOnly(True)
		self.label = QLabel("Purchase Stock:")

		# text inputs
		self.vbox1 = QVBoxLayout()
		self.vbox1.addWidget(self.label)
		self.vbox1.addWidget(self.log)
		self.vbox1.addWidget(QLabel("Enter Ticker of Stock to Buy:"))
		self.textfield = QTextEdit()
		self.vbox1.addWidget(self.textfield)
		self.vbox1.addWidget(QLabel("Enter Price Purchased at:"))
		self.textfield1 = QTextEdit()
		self.vbox1.addWidget(self.textfield1)
		self.vbox1.addWidget(QLabel("Enter Number of Shares Purchased:"))
		self.textfield2 = QTextEdit()
		self.vbox1.addWidget(self.textfield2)
		self.vbox1.addWidget(QLabel("Enter Purchase Date:"))


		# date field
		cur_date = QDate(datetime.datetime.now())
		self.date = QDateEdit(cur_date)
		self.vbox1.addWidget(self.date)

		enterbutton = QPushButton("Enter")
		enterbutton.clicked.connect(self.handleClick)
		self.vbox1.addWidget(enterbutton)
		self.setLayout(self.vbox1)
		self.resize(200, 100)
		self.show()

	def handleClick(self, event):
		ticker = self.textfield.toPlainText()
		price = self.textfield1.toPlainText()
		volume = self.textfield2.toPlainText()
		date = self.date.date()
		pydate = date.toPyDate()
		date = pydate.strftime('%Y/%m/%d')

		if doQuery(myConnection, "SELECT stock FROM stocks WHERE stock = '" + ticker + "'"):
			current_balance = doQuery(myConnection, "SELECT current_balance FROM users WHERE user_id = 1")
			if current_balance[0][0] > (float(price) * int(volume)):
				try:
					balance = int(current_balance[0][0]) - (float(price) * int(volume))
					doQuery(myConnection, "INSERT INTO Portfolio (user_id, stock, p_bought_at, volume, d_bought_at)" +
												"VALUES ('" + userId + "' ,'" + ticker + "', '" + price + "' , '" + volume + "', '" + date + "')")

					doQuery(myConnection, "UPDATE users SET current_balance = '" + str(balance) + "'WHERE user_id = " + userId)
					doQuery(myConnection, "UPDATE Portfolio SET d_bought_at = '" + date + "' WHERE stock = '" + ticker + "'")
					self.resultDialog("The stock has been successfully purchased. ""You're new account balance is: '" + str(balance) + "')")
				except ValueError:
					self.resultDialog("Please enter valid numbers for both price and volume.")
				except pymysql.InternalError:
					self.resultDialog("This is not a valid stock ticker. Please try again.")

				except pymysql.err.IntegrityError:
					cur_volume = doQuery(myConnection, "SELECT volume FROM portfolio WHERE user_id = " + userId + " AND stock = '" + ticker + "'")
					new_volume = int(volume) + int(cur_volume[0][0])
					doQuery(myConnection, "UPDATE Portfolio SET volume = '" + str(new_volume) + "' WHERE user_id = " + userId + " AND stock = '" + ticker + "'")
					doQuery(myConnection, "UPDATE Users SET current_balance = '" + str(balance) + "'WHERE user_id = " + userId)
					doQuery(myConnection, "UPDATE Portfolio SET d_bought_at = '" + date + "' WHERE user_id = " + userId + " AND stock = '" + ticker + "'")
					self.resultDialog(
						"The stock has been successfully purchased. ""You're new account balance is: '" + str(
							balance) + "')")

			else:
				self.resultDialog("Insufficient funds to buy this many shares. Please try again.")

		else:
			self.resultDialog("This is not a valid ticker. Please try again.")

	def resultDialog(self, result):
		dialog = BuyResultWindow(result, self)
		dialog.show()
		self.hide()

class SellResultWindow(QDialog):
	def __init__(self, result, parent=None):
		super(SellResultWindow, self).__init__(parent)
		self.grid = QGridLayout()
		self.grid.addWidget(QLabel("Stock Selling"), 0, 0)
		self.log = QTextEdit()
		self.log.setText(str(result))
		self.log.setReadOnly(True)
		self.grid.addWidget(self.log, 1, 0)
		self.button = QPushButton("Return To Homepage")
		self.button.clicked.connect(self.handleClick)
		self.button2 = QPushButton("Try Again")
		self.button2.clicked.connect(self.tryClick)
		self.grid.addWidget(self.button)
		self.grid.addWidget(self.button2)
		self.setLayout(self.grid)

	def handleClick(self, event):
		self.hide()
		return

	# button to go back to input window if needed (i.e. a typo is made by user)
	def tryClick(self, event):
		self.hide()
		self.sellwindow = SellWindow()
		self.sellwindow.show()
		return self.sellwindow

# Window for selling stock
class SellWindow(QDialog):
	def __init__(self, parent=None):
		super(SellWindow, self).__init__(parent)
		self.grid = QGridLayout()
		cur_balance = doQuery(myConnection, "SELECT current_balance FROM users WHERE user_id = " + userId)
		cur_balance = str(cur_balance[0][0])
		self.log = QLineEdit()
		self.log.setText("Current Balance: '" + cur_balance + "'")
		self.log.setReadOnly(True)
		self.label = QLabel("Sell Stock:")
		self.vbox1 = QVBoxLayout()
		self.vbox1.addWidget(self.label)
		self.vbox1.addWidget(self.log)
		self.vbox1.addWidget(QLabel("Enter Ticker of Stock to Sell:"))
		self.textfield = QTextEdit()
		self.vbox1.addWidget(self.textfield)
		self.vbox1.addWidget(QLabel("Enter Price Sold at:"))
		self.textfield1 = QTextEdit()
		self.vbox1.addWidget(self.textfield1)
		self.vbox1.addWidget(QLabel("Enter Number of Shares Sold"))
		self.textfield2 = QTextEdit()
		self.vbox1.addWidget(self.textfield2)
		self.vbox1.addWidget(QLabel("Enter Selling Date:"))

		# date field
		cur_date = QDate(datetime.datetime.now())
		self.date = QDateEdit(cur_date)
		self.vbox1.addWidget(self.date)
		enterbutton = QPushButton("Enter")
		enterbutton.clicked.connect(self.handleClick)
		self.vbox1.addWidget(enterbutton)
		self.setLayout(self.vbox1)
		self.show()

	def handleClick(self, event):
		ticker = self.textfield.toPlainText()
		price = self.textfield1.toPlainText()
		volume = self.textfield2.toPlainText()
		date = self.date.date()
		pydate = date.toPyDate()
		date = pydate.strftime('%Y/%m/%d')

		if doQuery(myConnection, "SELECT stock FROM stocks WHERE stock = '" + ticker + "'"):
			cur_balance = doQuery(myConnection, "SELECT current_balance FROM users WHERE user_id = 1")
			balance = int(cur_balance[0][0]) + (float(price) * int(volume))
			if doQuery(myConnection, "SELECT volume FROM portfolio WHERE stock = '" + ticker + "'"):
				cur_volume = doQuery(myConnection, "SELECT volume FROM portfolio WHERE stock = '" + ticker + "'")
				cur_volume = int(cur_volume[0][0])
				volume = cur_volume - int(volume)
				if volume == 0:
					doQuery(myConnection, "UPDATE users SET current_balance = '" + str(balance) + "'WHERE user_id = 1")
					return self.removeStock(ticker, "The stock has been successfully sold. You're new account balance is: '" + str(balance) + "'")
				elif volume > 0:
					try:
						doQuery(myConnection, "UPDATE users SET current_balance = '" + str(balance) + "'WHERE user_id = " + userId)
						doQuery(myConnection, "UPDATE portfolio SET volume = '" + str(volume) + 
							"' WHERE user_id = " + userId + " AND stock = '" + ticker + "'")
						self.resultDialog("The stock has been successfully sold. You're new account balance is: '" + str(balance) + "'")
					except pymysql.err.DataError:
						self.resultDialog("You do not own enough shares to sell this many. Please try again.")
					except ValueError:
						self.resultDialog("Please enter valid numbers for both price and volume.")
				elif volume < 0:
					self.resultDialog("You do not own enough shares to sell this many. Please try again.")

			else:
				self.resultDialog("You do not own this stock yet. Feel free to purchase it in the main window.")
		else:
			self.resultDialog("This is not a valid ticker. Please try again.")

	def resultDialog(self, result):
		dialog = SellResultWindow(result, self)
		dialog.show()
		self.hide()

	def removeStock(self, stock, result):
		doQuery(myConnection, "DELETE FROM Portfolio WHERE stock = '" + stock + "'")
		window.removeRow(stock)
		dialog = SellResultWindow(result, self)
		dialog.show()
		self.hide()


# Main Window
class Window(QWidget):
	def __init__(self, parent=None):
		super(Window, self).__init__(parent)

		self.login = LoginWindow(self)
		self.login.show()

		self.grid = QGridLayout()
		self.log = QTextEdit()
		self.table = QTableWidget(self.getPortfolioSize(), 7, self)
		self.table.setHorizontalHeaderLabels(["Stock Ticker", "Volume Owned", "Purchase Date", "Purchase Price",
											  "Current Price", "P/E Ratio", "Today's Change"])
		self.grid.addWidget(self.createButtonGroup())
		self.grid.addWidget(self.table)
		self.grid.addWidget(self.createRefreshButton())
		self.setLayout(self.grid)
		self.table.horizontalHeader().setStretchLastSection(True)
		self.table.resizeColumnsToContents()


		self.setWindowTitle("Portfolio Manager")
		self.resize(780, 320)

	def getPortfolioSize(self):

		stock_num = doQuery(myConnection, "SELECT COUNT(stock) FROM portfolio")
		stock_num = int(stock_num[0][0])
		return stock_num

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
		vbox.addWidget(self.table)
		vbox.addStretch()
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
		self.buywindow = BuyWindow()
		self.buywindow.show()
		return self.buywindow

	def handleSell(self, event):
		self.sellwindow = SellWindow()
		self.sellwindow.show()
		return self.sellwindow

	def getName(self,stock):
		name = doQuery(myConnection, "SELECT stock FROM stocks WHERE stock = '" + stock + "'")
		return str(name[0][0])


	def removeRow(self, stock):
		ans = self.table.findItems(str(stock), Qt.MatchExactly)
		row = self.table.row(ans[0])
		self.table.removeRow(row)
		return

	def handleRefresh(self, event):
		stocks = getStocks()
		rowPosition = self.table.rowCount()
		portSize = self.getPortfolioSize()
		if rowPosition < portSize:
			self.table.insertRow(rowPosition)
			self.handleRefresh(event)

		elif rowPosition >= portSize:
			c = 0
			for s in stocks:
				volume = doQuery(myConnection,"SELECT volume FROM Portfolio WHERE stock = '" + s + "'")
				volume = str(volume[0][0])
				price = doQuery(myConnection, "SELECT p_bought_at FROM Portfolio WHERE stock = '" + s + "'")
				price = str(price[0][0])
				date = doQuery(myConnection, "SELECT d_bought_at FROM Portfolio WHERE stock = '" + s + "'")
				date = str(date[0][0])
				self.table.setItem(c, 0, QTableWidgetItem(s))
				self.table.setItem(c, 1, QTableWidgetItem(volume))
				self.table.setItem(c, 2, QTableWidgetItem(date))
				self.table.setItem(c, 3, QTableWidgetItem(price))
				s = Share(s)
				self.table.setItem(c, 4, QTableWidgetItem(s.get_price()))
				self.table.setItem(c, 6, QTableWidgetItem(s.get_change_percent_change()))
				self.table.setItem(c, 5, QTableWidgetItem(s.get_price_earnings_ratio()))

				c = c + 1


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = Window()
	sys.exit(app.exec_())
