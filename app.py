#подключение библиотек
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,QHBoxLayout
from random import randint
def show_winner():
    winner.setText('Победитель:')
    random_num = str(randint(1,100))
    answer.setText(random_num)
#создание элементов интерфейса
app = QApplication([])
main_win = QWidget()
#пиши код здесь
main_win.setWindowTitle('Привет, PyQT')
main_win.move(900,70)
main_win.resize(400,20)
winner = QLabel('Нажмите, чтобы узнать победителя')
answer = QLabel('?')
button = QPushButton('Сгенерировать')
button.clicked.connect(show_winner)
v_line = QVBoxLayout()
v_line.addWidget(winner, alignment = Qt.AlignCenter)
v_line.addWidget(answer, alignment = Qt.AlignCenter)
v_line.addWidget(button, alignment = Qt.AlignCenter)
main_win.setLayout(v_line)
main_win.show()
app.exec_()