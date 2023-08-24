import face_recognition as fr
import numpy as np
import urllib.request
import base64
import requests

class Faces:
    def __init__(self, Aluno, Dados):
        self.aluno = Aluno
        self.face = self.ExtrairFace()
        self.dados = Dados
        self.faces_armazenadas = "data/backup/faces.npz"
        # self.api = "https://web-production-9f8c8.up.railway.app/reconhecimento"
        self.api = "http://localhost:8080/reconhecimento"

    def ExtrairFace(self):
        imagem = self.importaImagem()
        aluno = fr.load_image_file(imagem)
        face = fr.face_encodings(aluno)[0]
        return face
            
    def importaImagem(self):
        caminhoDaImagem = "data/imagens/%s.jpg" % self.aluno.matricula
        urllib.request.urlretrieve(self.aluno.foto, caminhoDaImagem)
        return caminhoDaImagem

    def armazenarFace(self):
        print('Armazenando Face')
        # ARMAZENAMENTO LOCAL:

        try:
            backup = np.load(self.faces_armazenadas) 
        except:
            np.savez(self.faces_armazenadas, np.array([]))
            backup = np.load(self.faces_armazenadas)

        faces = []

        # Armazena na lista de faces todas os objetos (faces) não nulas que estão na variável de backup
        for item in backup.files:
            if (backup[item] != []): 
                faces.append(backup[item])
        
        faces.append(self.face)
        np.savez(self.faces_armazenadas, *faces)

        # Abaixo adiciona-se o nome e a matrícula dos alunos em um arquivo local no seguinte formato: matricula1:aluno1/matricula2:aluno2/.../matriculaN:alunoN/
        with open("data/backup/nomes.txt", "a") as arquivo:
            arquivo.write("%s:%s/" % (self.aluno.matricula, self.aluno.nome))

        # ARMAZENAMENTO DAS FACES NO SERVIDOR:

        tobase64 = base64.b64encode(self.face)

        # Atualiza o servidor com os códigos faciais em base64 e atualiza a informação de que o aluno agora já tem seu código facial cadastrado
        requests.patch("%s/id/%s" % (self.api, self.aluno.matricula),{"caracteres": tobase64, "registered": True},)

    def atualizarFace(self):
        print('Atualizanco Face')
        backup = np.load(self.faces_armazenadas)
        faces = []
        for item in backup.files:
            if backup[item] != []:
                faces.append(backup[item])

        matriculaAluno = self.dados.matriculas

        indexAluno = matriculaAluno.index(self.aluno.matricula)

        faces[indexAluno] = self.face
        np.savez(self.faces_armazenadas, *faces)

        tobase64 = base64.b64encode(self.face)

        requests.patch("{}/atualized/id/{}".format(self.api, self.aluno.matricula),{"atualized": False, "caracteres": tobase64})

