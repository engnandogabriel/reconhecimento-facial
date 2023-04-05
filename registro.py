import requests
import datetime

from model import Aluno


class Registro:
    def __init__(self, dados):
        self.dados = dados
        self.aSeremRegistrados = []
        self.aSeremAtualizados = []
        self.Alunos = []
        self.api = "https://web-production-9f8c8.up.railway.app/reconhecimento"

    def confirmaPresenca(self, id, matricula):
        print(id)
        print(matricula)

        if (self.Alunos[id].controleFrequencia == 0 and self.Alunos[id].verificaPresenca() == 0):
            currentDataBase = datetime.datetime.now()
            print("CurrentDataBase: {}".format(currentDataBase))
            dateUser = self.dados.get_data_complete()
            print("DataUser: {}".format(dateUser))
            self.Alunos[id].controleFrequencia = 1
            print('Registrando Frequência')
            requests.patch("%s/registrarfrequencia/%s" % (self.api, matricula),{"atualizedAt": currentDataBase, "dateUser": dateUser},)
        else:
            print("Cadastro Realizado com suscesso")

    def verificaAtualizacao(self):
        for aluno in self.Alunos:
            if aluno.atualized == True:
                self.aSeremAtualizados.append(aluno)
        if len(self.aSeremAtualizados) == 0:
            print("Nenhum aluno a ser atualizado")
            return False
        else:
            print("{} a serem atualizado".format(len(self.aSeremAtualizados)))
            return True

    def verificaRegistro(self):
        requisicao = self.dados.get_dados()
        for registro in requisicao:
            aluno = Aluno(registro, self.dados)
            self.Alunos.append(aluno)
            if aluno.registered is False:
                self.aSeremRegistrados.append(aluno)
        if len(self.aSeremRegistrados) == 0:
            print("Nenhum aluno a ser registrado")
            return False 
        else:
            print("{} a serem registrado".format(len(self.aSeremRegistrados)))
            return True
