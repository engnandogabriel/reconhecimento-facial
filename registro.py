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
        self.Alunos = []
        self.faces = Faces
        # self.api = "https://web-production-9f8c8.up.railway.app/reconhecimento"
        self.api = "http://localhost:8080/reconhecimento"

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
            print("Cadastro Ja realizado")

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
            if aluno.registered is False and aluno.foto != "":
                self.aSeremRegistrados.append(aluno)
        if len(self.aSeremRegistrados) == 0:
            print("Nenhum aluno a ser registrado")
            return False 
        else:
            print("{} a serem registrado".format(len(self.aSeremRegistrados)))
            return True
        
    def verificaExclusao(self):
        pass
        # requisicao = self.dados.get_dados()

        # print(self.Alunos)

        # for i in range(len(self.Alunos)):
        #     if(requisicao[i]['matricula'] == self.Alunos.nome[i]):
        #         print('certo')
        # cont = 0
        # for aluno in self.Alunos:
        #     if(requisicao[cont]['matricula'] in aluno.matricula ):
        #         print(aluno.nome)
        #         print(cont)
        #     print(aluno.matricula)
        #     # print(requisicao[cont]['nome'])
        #     # print(aluno.nome)
        #     cont+=1
        # faces_armazenadas = "data/backup/faces.npz"
        # try:
        #     backup = np.load(faces_armazenadas)  # As faces ficarão em um dicionário base do numpy. Para mais informações pesquise sobre o np.load em arquivos .npz
        # except:
        #     np.savez(faces_armazenadas, np.array([]))  # Cria-se um arquivo .npz que armazena apenas um array vazio que DEVE ser removido a seguir
        #     backup = np.load(faces_armazenadas)

        # faces = []  # Lista que vai armazenar todos os códigos faciais

        # # Armazena na lista de faces todas os objetos (faces) não nulas que estão na variável de backup
        # for item in backup.files:
        #     if (backup[item] != []):  # Verifica se o objeto não é vazio. Essa verificação é feita para o caso do try..except acima.
        #         faces.append(backup[item])
        # print(len(faces))