from PyQt5.QtWidgets import *
from PyQt5.uic import *
from PyQt5.QtCore import *
from PyQt5 import QtSql

global shot
shot = -1

class MyApp(QMainWindow):
	def __init__(self):
		super().__init__()
		loadUi("hi.ui", self)

		self.db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
		self.db.setHostName("3.35.8.78")
		self.db.setDatabaseName("DB_16_03")
		self.db.setUserName("SSAFY16_03_2")
		self.db.setPassword("1234")
		ok = self.db.open()
		print(ok)
		if ok == False:return

		self.query = QtSql.QSqlQuery("delete from command2")
		self.query = QtSql.QSqlQuery("delete from sensing2")

		self.query = QtSql.QSqlQuery()
		self.timer1 = QTimer()
		self.timer1.setInterval(100)
		self.timer1.timeout.connect(self.pollingQuery)
		self.timer1.start()
		
	def pollingQuery(self):
		# command log
		self.query = QtSql.QSqlQuery("select * from command2 order by time desc limit 8")
		str = ""

		self.cmd_text.clear()
		while (self.query.next()):
			self.record = self.query.record()
			str += "%s | %10s | %10s | %4d\n" % (self.record.value(0).toString(), self.record.value(1), self.record.value(2), self.record.value(3))
			self.cmd_text.appendPlainText(str)
			
		self.cmd_text.setPlainText(str)
		
		# sensing log
		self.query = QtSql.QSqlQuery("select * from sensing2 order by time desc limit 8")
		str = ""
		
		self.sen_text.clear()
		
		global shot
		if self.query.next():
			self.record = self.query.record()
			str += "%s | %10s | %10s | %10s\n" % (self.record.value(0).toString(), self.record.value(1), self.record.value(2), self.record.value(3))
			shot = int(self.record.value(1))
		
		while (self.query.next()):
			self.record = self.query.record()
			str += "%s | %10s | %10s | %10s\n" % (self.record.value(0).toString(), self.record.value(1), self.record.value(2), self.record.value(3))
		
		if shot == 1:
			self.shot_check.setText("Nice shot!!")
		elif shot == 0:
			self.shot_check.setText("Miss~~")
		else:
			self.shot_check.setText("")

		self.sen_text.setPlainText(str)

	def commandQuery(self, cmd, arg):
		self.query.prepare("insert into command2 (time, cmd_string, arg_string, is_finish) values (:time, :cmd, :arg, :finish)")
		time = QDateTime().currentDateTime()
		self.query.bindValue(":time", time)
		self.query.bindValue(":cmd", cmd)
		self.query.bindValue(":arg", arg)
		self.query.bindValue(":finish", 0)
		self.query.exec()

	def clickedRight(self):
		self.commandQuery("right", "1 sec")

	def clickedLeft(self):
		self.commandQuery("left", "1 sec")

	def clickedGo(self):
		self.commandQuery("go", "1 sec")

	def clickedBack(self):
		self.commandQuery("back", "1 sec")

	def clickedMid(self):
		self.commandQuery("mid", "1 sec")

	def clickedStop(self):
		self.commandQuery("stop", "")

	def clickedShoot(self):
		self.commandQuery("shoot", "")

	def frontPress(self):
		self.commandQuery("front", "press")

	def frontRelease(self):
		self.commandQuery("front", "release")

	def rightPress(self):
		self.commandQuery("rightside", "press")

	def rightRelease(self):
		self.commandQuery("rightside", "release")

	def leftPress(self):
		self.commandQuery("leftside", "press")

	def leftRelease(self):
		self.commandQuery("leftside", "release")

	def barrelLeftPress(self):
		self.commandQuery("barrelleft", "press")

	def barrelLeftRelease(self):
		self.commandQuery("barrelleft", "release")

	def barrelRightPress(self):
		self.commandQuery("barrelright", "press")

	def barrelRightRelease(self):
		self.commandQuery("barrelright", "release")

app = QApplication([])
win = MyApp()
win.show()
app.exec()
