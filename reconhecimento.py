from multiprocessing.pool import ThreadPool
import cv2
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
        self.dados = DadosGerais()
        self.nome = None
        self.matricula = None
        self.curso = None
        self.hora = None
        self.registrado = None
        self.localizacoesFaces = None
        self.registro = Registro(self.dados)
        self.formulario = formulario
        self.timer = QTimer()
        self.timer.timeout.connect(self.threaFuncion)
        # self.api = "http://localhost:8080/reconhecimento"
        self.api = "https://web-production-9f8c8.up.railway.app/reconhecimento"


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
                    self.nome = alunos[primeiraCorresponcia].nome    
                    self.matricula = alunos[primeiraCorresponcia].matricula
                    self.curso = alunos[primeiraCorresponcia].curso
                    try:
                        hora = alunos[primeiraCorresponcia].frequencia[-1]
                        self.hora = hora.split('T')[1]
                    except:
                        hora = '00h00'
                    print(hora)
                    self.registrado = 'Registrado'

                    self.registro.confirmaPresenca(primeiraCorresponcia,self.matricula)
                    if self.nome and self.matricula and self.curso and self.hora:
                        self.exebirDadosInterfcae()

                nomeFaces.append(nome)
            return
    
    def exebirDadosInterfcae(self):
        self.formulario.recebe_nome.setText(self.nome)
        self.formulario.recebe_matricula.setText(self.matricula)
        self.formulario.recebe_curso.setText(self.curso)
        self.formulario.recebe_status.setText(self.registrado)
        self.formulario.recebe_horario.setText(self.hora)


    def reconhecimento(self):
        self.camera.start_movie()
        self.timer.start(2500)

    def threaFuncion(self):
        self.localizacoesFaces = fr.face_locations(self.camera.TratarFrame())
        if self.localizacoesFaces:
            pool = QThreadPool.globalInstance()
            recoThread = ReconhecimentoThread(self)
            pool.start(recoThread)
        else:
            self.nome = None
            self.matricula = None
            self.curso = None
            self.hora = None
            self.registrado = None
            self.exebirDadosInterfcae()

   
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
                    print(f'Aluno {aluno.nome} não pode ser registrado')
                    requests.patch("%s/id/%s" % (self.api, aluno.matricula),{"registered": True})
        


        self.dados.ImportarAlunos()
        # Se houver nescessidade de atualização, a rotina é acionada
        if self.registro.verificaAtualizacao():
            for aluno in self.registro.aSeremAtualizados:
                face = Faces(aluno, self.dados)
                face.atualizarFace()
        
class ReconhecimentoThread(QRunnable):
    def __init__(self, reconhecimento) -> None:
        super().__init__()
        self.reconhecimento = reconhecimento

    def run(self) -> None:
        self.reconhecimento.start_recognition()