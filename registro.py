import requests
import datetime
import numpy as np

from model import Aluno
from Faces import Faces

class Registro:
    def __init__(self, dados):
        self.dados = dados
        self.aSeremRegistrados = []
        self.aSeremAtualizados = []
        self.erroRegistro = []
        self.Alunos = []
        self.faces = Faces
        # self.api = "https://web-production-9f8c8.up.railway.app/reconhecimento"
        self.api = "http://localhost:8080/reconhecimento"

    def confirmaPresenca(self, id, matricula):

        if (self.Alunos[id].controleFrequencia == 0 and self.Alunos[id].verificaPresenca() == 0):
            currentDataBase = datetime.datetime.now()
            dateUser = self.dados.get_data_complete()
            self.Alunos[id].controleFrequencia = 1
            print('Registrando Frequência')
            requests.patch("%s/registrarfrequencia/%s" % (self.api, matricula),{"atualizedAt": currentDataBase, "dateUser": dateUser},)
        else:
            print("Cadastro Ja realizado")

    def verificaAtualizacao(self):
        for aluno in self.Alunos:
            if aluno.atualized == True:
                self.aSeremAtualizados.append(aluno)
        if len(self.aSeremAtualizados) == 0:
            print("Nenhum aluno a ser atualizado")
            return False
        elif len(self.aSeremAtualizados) > 1:
            print("{} a serem atualizado".format(len(self.aSeremAtualizados)))
            return True
        else:
            print('1 aluno a ser atualizado')
            return True

    def verificaRegistro(self):
        requisicao = self.dados.get_dados()
        for registro in requisicao:
            aluno = Aluno(registro, self.dados)
            self.Alunos.append(aluno)
            if aluno.registered is False and aluno.foto != "":
                self.aSeremRegistrados.append(aluno)
            elif aluno.foto == '':
                self.erroRegistro.append(aluno.nome)
            
        if(len(self.erroRegistro)>0):
            for c in self.erroRegistro:
                print(f'Aluno {c} não pode ser registrado')

        if len(self.aSeremRegistrados) == 0:
            print("Nenhum aluno a ser registrado")
            return False 
        elif len(self.aSeremAtualizados) > 1:
            print("{} a serem atualizado".format(len(self.aSeremRegistrados)))
            return True
        else:
            print('1 aluno a ser atualizado')
            return True