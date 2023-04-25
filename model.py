import numpy as np
import cv2
import requests

import datetime

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, QTimer, QRunnable
from PyQt5 import QtGui

class Camera:
    def __init__(self, cam_num, formulario):
        self.cap = cv2.VideoCapture(cam_num)
        self.formulario = formulario
        self.last_frame = None
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_movie)

    def get_frame(self):
        ret, self.last_frame = self.cap.read()
        return self.last_frame

    def show_camera(self):
        cv2.imshow("Video da webcam", self.last_frame)

    def acquire_movie(self, num_frames):
        movie = []
        for _ in range(num_frames):
            movie.append(self.get_frame())
        return movie

    def stop_camera(self):
        self.cap.release()

    def TratarFrame(self):
        # Reduz o tamanho do Frame para aprimorar performance
        frame_formatado = cv2.resize(self.get_frame(), (0, 0), fx=0.5, fy=0.5)
        frame_formatado = frame_formatado[
            :, :, :: 1
        ]  # Altera o padrão de cores para rgb
        return frame_formatado
    
    def update_movie(self):
        frame = self.TratarFrame()
        larg = 480
        alt = int(frame.shape[0]/frame.shape[1]*larg)
        frame = cv2.resize(frame, (larg, alt), interpolation = cv2.INTER_AREA)
        height, width, channel = frame.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.formulario.camera.setPixmap(QtGui.QPixmap(qImg))

    def start_movie(self):
        self.movie_thread = MovieThread(self)
        self.movie_thread.start()
        self.update_timer.start(30)

class MovieThread(QThread):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    def run(self):
        self.camera.acquire_movie(200)

class Aluno:
    def __init__(self, dict, dados):
        self.id = dict["_id"]
        self.nome = dict["nome"]
        self.matricula = dict["matricula"]
        self.foto = dict["foto"]
        self.frequencia = dict["frequencia"]
        self.atualizedAt = dict["atualizedAt"].split("T")[0]
        self.registered = dict["registered"]
        self.atualized = dict["atualized"]
        self.controleFrequencia = 0
        self.dados = dados

    def verificaPresenca(self):
        tamanhoFrequencia = len(self.frequencia)
        # 2023-03-02T14:01:17.402+00:00
        if len(self.frequencia) != 0:
            ultimaFrequenica = self.frequencia[tamanhoFrequencia - 1]
            ultimaFrequenica = ultimaFrequenica.split("T")[0]
        else:
            ultimaFrequenica = "0000-00-00"

        if tamanhoFrequencia == 0:
            print("Cadastro de frequencia nescessário")
            self.controleFrequencia = 0
            return 0

        elif self.atualizedAt == self.dados.get_data():
            print("Cadastro de frequência ja realizado")
            self.controleFrequencia = 1
            return 1

        elif ultimaFrequenica == self.dados.get_data():
            print("Cadastro de frequência ja realizado")
            self.controleFrequencia = 1
            return 1
        else:
            print("Cadastro nescessário")
            self.controleFrequencia = 0
            return 0


class DadosGerais:
    def __init__(self):
        # self.api = "https://web-production-9f8c8.up.railway.app/reconhecimento"
        self.api = "http://localhost:8080/reconhecimento"
        self.requisicao = requests.get(self.api).json()
        self.nomes = []
        self.matriculas = []

    def get_data(self):
        currentDate = datetime.date.today()  # recupera o dia atual
        currentDate = currentDate.strftime("%Y-%m-%d")  # converter para string
        return currentDate

    def get_data_complete(self):
        dateComplete = datetime.datetime.now()
        dateComplete = dateComplete.strftime("%Y-%m-%dT%H:%M")
        return dateComplete

    def ImportarAlunos(self):
        with open("data/backup/nomes.txt", "r") as arquivo:
            texto = arquivo.read()
            arquivo.close()

            alunos = texto.split(
                "/"
            )  # Divide o arquivo em uma lista com a seguinte estrutura: [matricula1:aluno1, matricula2:aluno2,..., matriculaN:alunoN, NULL]
            alunos.pop()  # Remove o valor nulo da última posição da lista
            # Separa cada item da lista alunos em dois: matricula, nome. Em seguida, armazena na variável nomes apenas o nome do aluno
            for aluno in alunos:
                self.matriculas.append(aluno.split(":")[0])
                self.nomes.append(aluno.split(":")[1])

    def importaFaces(self):
        backup = np.load("data/backup/faces.npz")
        faces = []

        for item in backup.files:
            if backup[item] != []:
                faces.append(backup[item])
        return faces

    def get_dados(self):
        return self.requisicao
