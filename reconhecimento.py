import numpy as np
import os
import face_recognition as fr
import cv2
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, QTimer
from PyQt5 import QtGui

import threading

from model import Aluno
from model import DadosGerais
from Faces import Faces
from registro import Registro


import requests


class Reconhecimento:
    def __init__(self, camera, formulario):
        self.camera = camera
        self.dados = DadosGerais()
        self.registro = Registro(self.dados)
        self.formulario = formulario
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_movie)
      

    def update_image(self):
        frame = self.camera.get_frame()
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.formulario.camera.setPixmap(QtGui.QPixmap(qImg))

    def update_movie(self):
        frame = self.start_recognition()
        larg = 720
        alt = int(frame.shape[0]/frame.shape[1]*larg)
        frame = cv2.resize(frame, (larg, alt), interpolation = cv2.INTER_AREA)
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.formulario.camera.setPixmap(QtGui.QPixmap(qImg))

    def start_movie(self):
        self.movie_thread = MovieThread(self.camera)
        self.movie_thread.start()
        self.update_timer.start(30)

    def stop_movie(self):
        self.camera.stop_camera()

    def teste(self):
        print('TESTANDO')

    # inicia a câmera
    def start_recognition(self):
        processo = True
        # frame_formatado = self.camera.get_frame()
        frame_formatado = self.camera.TratarFrame()
        while True:
            facesConhecidas = self.dados.importaFaces()
            alunos = self.registro.Alunos

            if processo is True:

                localizacoesFaces = fr.face_locations(frame_formatado)
                faces = fr.face_encodings(frame_formatado, localizacoesFaces)
                nomeFaces = []
                for face in faces:
                    correspodem = fr.compare_faces(facesConhecidas, face, tolerance=0.45)
                    nome = "Desconhecido"

                    if True in correspodem:
                        primeiraCorresponcia = correspodem.index(True)
                        print(primeiraCorresponcia)
                        nome = alunos[primeiraCorresponcia].nome
                        print(nome)
                        matricula = alunos[primeiraCorresponcia].matricula
                        threading.Thread(target = self.registro.confirmaPresenca, args=(primeiraCorresponcia,matricula)).start()
                        # threading.Thread(target= self.teste).start()

                    nomeFaces.append(nome)
            
            return frame_formatado


    def main(self):
        # Se houver necessidade de cadastro, a rotina é acionada
        if self.registro.verificaRegistro():
            # Extrai a face de cada aluno que deve ser atualizado e faz seu armazenamento
            for aluno in self.registro.aSeremRegistrados:
                face = Faces(aluno, self.dados)
                face.armazenarFace()
        self.dados.ImportarAlunos()

        # Se houver nescessidade de atualização, a rotina é acionada
        if self.registro.verificaAtualizacao():
            for aluno in self.registro.aSeremAtualizados:
                face = Faces(aluno, self.dados)
                face.atualizarFace()

class MovieThread(QThread):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    def run(self):
        self.camera.acquire_movie(200)