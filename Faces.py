import face_recognition as fr
import numpy as np
import urllib.request
import base64
import requests


from model import Aluno
from model import DadosGerais


class Faces:
    def __init__(self, Aluno, Dados):
        self.aluno = Aluno
        self.face = self.ExtrairFace()
        self.dados = Dados
        self.faces_armazenadas = "data/backup/faces.npz"
        self.api = "https://web-production-9f8c8.up.railway.app/reconhecimento"

    def ExtrairFace(self):
        imagem = self.importaImagem()  # Armazena o caminho da foto na variável
        aluno = fr.load_image_file(imagem)  # Carrega a imagem para o código
        face = fr.face_encodings(aluno)[0]  # Extrai, de fato, a face da imagem carregada
        return face

    def importaImagem(self):
        caminhoDaImagem = "data/imagens/%s.jpg" % self.aluno.matricula
        urllib.request.urlretrieve(self.aluno.foto, caminhoDaImagem)
        return caminhoDaImagem

    def armazenarFace(self):
        # ARMAZENAMENTO LOCAL:

        try:
            backup = np.load(self.faces_armazenadas)  # As faces ficarão em um dicionário base do numpy. Para mais informações pesquise sobre o np.load em arquivos .npz
        except:
            np.savez(self.faces_armazenadas, np.array([]))  # Cria-se um arquivo .npz que armazena apenas um array vazio que DEVE ser removido a seguir
            backup = np.load(self.faces_armazenadas)

        faces = []  # Lista que vai armazenar todos os códigos faciais

        # Armazena na lista de faces todas os objetos (faces) não nulas que estão na variável de backup
        for item in backup.files:
            if (backup[item] != []):  # Verifica se o objeto não é vazio. Essa verificação é feita para o caso do try..except acima.
                faces.append(backup[item])

        faces.append(self.face)  # Adiciona-se a face a ser armazenada (que foi passada como parâmetro) na lista de faces
        np.savez(self.faces_armazenadas, *faces)  # Salva a lista de faces (atualizada com a nova) no arquivo .npz

        # Abaixo adiciona-se o nome e a matrícula dos alunos em um arquivo local no seguinte formato: matricula1:aluno1/matricula2:aluno2/.../matriculaN:alunoN/
        with open("data/backup/nomes.txt", "a") as arquivo:
            arquivo.write("%s:%s/" % (self.aluno.matricula, self.aluno.nome))

        # ARMAZENAMENTO DAS FACES NO SERVIDOR:

        tobase64 = base64.b64encode(self.face)  # Converte a face para uma string codificada usando base64.

        # Atualiza o servidor com os códigos faciais em base64 e atualiza a informação de que o aluno agora já tem seu código facial cadastrado
        requests.patch("%s/id/%s" % (self.api, self.aluno.matricula),{"caracteres": tobase64, "registered": True},)

    def atualizarFace(self):
        backup = np.load(self.faces_armazenadas)

        faces = []

        for item in backup.files:
            if backup[item] != []:
                faces.append(backup[item])

        matriculaAluno = self.dados.matriculas

        sentinela = matriculaAluno.index(self.aluno.matricula)

        faces[sentinela] = self.face
        np.savez(self.faces_armazenadas, *faces)

        tobase64 = base64.b64encode(self.face)

        requests.patch("{}/atualized/id/{}".format(self.api, self.aluno.matricula),{"atualized": False, "caracteres": tobase64})

    def verificaPresenca(self):
        print(self.aluno.get_dados)
