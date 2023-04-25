from model import Camera
from reconhecimento import Reconhecimento
from reconhecimento import ReconhecimentoThread
from PyQt5 import uic, QtWidgets
# from PyQt5.QtWidgets import QApplication, QPushButton, QAction


app = QtWidgets.QApplication([])
formulario = uic.loadUi('tela.ui')

camera = Camera(0, formulario)

reconhecimento_facial = Reconhecimento(camera, formulario)


#acoes da interface
formulario.atualizar.clicked.connect(reconhecimento_facial.main)
formulario.start.clicked.connect(camera.start_movie)
# formulario.pause.clicked.connect(reconhecimento_facial.executar)
formulario.pause.clicked.connect(reconhecimento_facial.reconhecimento)


formulario.show()
app.exec()
