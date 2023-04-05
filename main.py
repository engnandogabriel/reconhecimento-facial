from model import Camera
from reconhecimento import Reconhecimento
from PyQt5 import uic, QtWidgets
# from PyQt5.QtWidgets import QApplication, QPushButton, QAction


app = QtWidgets.QApplication([])
formulario = uic.loadUi('tela.ui')

camera = Camera(0)

reconhecimento_facial = Reconhecimento(camera, formulario)


#acoes da interface
formulario.atualizar.clicked.connect(reconhecimento_facial.main)
formulario.start.clicked.connect(reconhecimento_facial.start_movie)
formulario.pause.clicked.connect(reconhecimento_facial.stop_movie)


formulario.show()
app.exec()
