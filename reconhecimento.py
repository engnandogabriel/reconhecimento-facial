from multiprocessing.pool import ThreadPool
import time
import numpy as np
import face_recognition as fr
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, QTimer, QRunnable, QThreadPool
from PyQt5 import QtGui


from model import Aluno
from model import DadosGerais
from Faces import Faces
from registro import Registro


import requests


class Reconhecimento:
    def __init__(self, camera, formulario):
        self.camera = camera
        self.ignorado = []
        self.dados = DadosGerais()
        self.registro = Registro(self.dados)
        self.formulario = formulario
        self.timer = QTimer()
        self.timer.timeout.connect(self.executar)
        self.api = "http://localhost:8080/reconhecimento"


    # inicia a câmera
    def start_recognition(self):
        processo = True
        frame_formatado = self.camera.TratarFrame()
        
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
                    self.registro.confirmaPresenca(primeiraCorresponcia,matricula)

                nomeFaces.append(nome)
            return
                
    def reconhecimento(self):
        self.timer.start(2000)

    def executar(self):
        # camThread = self.camera.start_movie()
        # pool.start(camThread)
        # self.camera.start_movie()

        localizacoesFaces = fr.face_locations(self.camera.TratarFrame())
        print(localizacoesFaces)

        if localizacoesFaces:
            print('tem pessoa')
            pool = QThreadPool.globalInstance()
            recoThread = ReconhecimentoThread(self)
            pool.start(recoThread)
            print("teste")
        else:
            pass

    def main(self):
        # Se houver necessidade de cadastro, a rotina é acionada
        if self.registro.verificaRegistro():
            # Extrai a face de cada aluno que deve ser atualizado e faz seu armazenamento
            for aluno in self.registro.aSeremRegistrados:
                try:
                    face = Faces(aluno, self.dados)
                    print(f'{aluno.nome} sendo registrado')
                    face.armazenarFace()
                except:
                    requests.patch("%s/id/%s" % (self.api, aluno.matricula),{"registered": True})
                    self.ignorado.append(aluno)

        for c in self.ignorado:
            print(c.nome)
        self.dados.ImportarAlunos()

        # Se houver nescessidade de atualização, a rotina é acionada
        if self.registro.verificaAtualizacao():
            for aluno in self.registro.aSeremAtualizados:
                face = Faces(aluno, self.dados)
                face.atualizarFace()
    
        # remover aluno
        # self.registro.verificaExclusao()
        
class ReconhecimentoThread(QRunnable):
    def __init__(self, reconhecimento) -> None:
        super().__init__()
        print("construtor")
        self.reconhecimento = reconhecimento

    def run(self) -> None:
        self.reconhecimento.start_recognition()