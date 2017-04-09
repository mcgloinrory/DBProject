#!/usr/bin/python

import sys
import time
import datetime


import pymysql
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
							 QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QTextEdit, QHBoxLayout,
							 QLineEdit, QDialog, QLabel, QDateEdit)


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
	for stock in doQuery(myConnection, 'SELECT stock FROM Stocks'):
		shares.append(stock[0])
	return shares


# Get most recent date historical_data was refreshed
def getRecentDate():
	return str(doQuery(myConnection, 'SELECT most_recent_data()')[0][0])



# Window to show the results of info check
class InfoResultWindow(QDialog):
	def __init__(self, result, parent=None):
		super(InfoResultWindow, self).__init__(parent)

		self.grid = QGridLayout()
		self.grid.addWidget(QLabel("Company Info"), 0, 0)
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
		result = doQuery(myConnection, "SELECT s.name FROM Stocks s WHERE s.stock = '" + ticker + "'")
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
		cur_balance = doQuery(myConnection, "SELECT current_balance FROM users WHERE user_id = 1")
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
			if current_balance[0][0] > (int(price) * int(volume)):

				try:
					balance = int(current_balance[0][0]) - (int(price) * int(volume))
					doQuery(myConnection, "INSERT INTO Portfolio (user_id, stock, p_bought_at, volume, d_bought_at)" +
												"VALUES (1 ,'" + ticker + "', '" + price + "' , '" + volume + "', '" + date + "')")
					doQuery(myConnection, "UPDATE users SET current_balance = '" + str(balance) + "'WHERE user_id = 1")
					doQuery(myConnection, "UPDATE Portfolio SET d_bought_at = '" + date + "' WHERE stock = '" + ticker + "'")

					self.resultDialog("The stock has been successfully purchased. "
									  "You're new account balance is: '" + str(balance) + "')")

				except pymysql.InternalError:
					self.resultDialog("This is not a valid stock ticker. Please try again.")

				except pymysql.err.IntegrityError:
					cur_volume = doQuery(myConnection, "SELECT volume FROM portfolio WHERE stock = '" + ticker + "'")
					new_volume = int(volume) + int(cur_volume[0][0])
					doQuery(myConnection, "UPDATE Portfolio SET volume = '" + str(new_volume) + "' WHERE stock = '" + ticker + "'")
					doQuery(myConnection, "UPDATE Users SET current_balance = '" + str(balance) + "'WHERE user_id = 1")
					doQuery(myConnection, "UPDATE Portfolio SET d_bought_at = '" + date + "' WHERE stock = '" + ticker + "'")
					self.resultDialog("The stock has been successfully purchased. You're new account balance is: '" + str(balance) + "')")

				except ValueError:
					self.resultDialog("Please enter valid numbers for both price and volume.")

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
		cur_balance = doQuery(myConnection, "SELECT current_balance FROM users WHERE user_id = 1")
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
			balance = int(cur_balance[0][0]) + (int(price) * int(volume))
			if doQuery(myConnection, "SELECT volume FROM portfolio WHERE stock = '" + ticker + "'"):
				cur_volume = doQuery(myConnection, "SELECT volume FROM portfolio WHERE stock = '" + ticker + "'")
				cur_volume = int(cur_volume[0][0])
				if cur_volume >= int(volume):
					volume = cur_volume - int(volume)
					try:
						doQuery(myConnection, "UPDATE users SET current_balance = '" + str(balance) + "'WHERE user_id = 1")
						doQuery(myConnection, "UPDATE portfolio SET volume = '" + str(volume) + "' WHERE stock = '" + ticker + "'")
						self.resultDialog("The stock has been successfully sold. You're new account balance is: '" + str(balance) + "'")

					except pymysql.err.DataError:
						self.resultDialog("You do not own enough shares to sell this many. Please try again.")
					except ValueError:
						self.resultDialog("Please enter valid numbers for both price and volume.")
				else:
					self.resultDialog("You do not own enough shares to sell this many. Please try again.")
			else:
				self.resultDialog("You do not own this stock yet. Feel free to purchase it on the homepage.")
		else:
			self.resultDialog("This is not a valid ticker. Please try again.")

	def resultDialog(self, result):
		dialog = SellResultWindow(result, self)
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
		self.buywindow = BuyWindow()
		self.buywindow.show()
		return self.buywindow

	def handleSell(self, event):
		self.sellwindow = SellWindow()
		self.sellwindow.show()
		return self.sellwindow

	def handleRefresh(self, event):
		lastDate = getRecentDate()
		shares = getStocks()
		for s in shares:
			share = Share(s)
			try:
				for stock in share.get_historical(lastDate, time.strftime("%Y-%m-%d")):
					doQuery(myConnection,
							"INSERT INTO `Historical_Data` (`date`, `stock`, `adj_closed`) VALUES ('" + stock[
								'Date'] + "', '" + stock['Symbol'] + "', '" + stock['Adj_Close'] + "')")
			except:
				print('Error encountered')
		return


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec_())
