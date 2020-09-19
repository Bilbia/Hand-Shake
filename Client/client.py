#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação Client
####################################################

from enlace import *
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import math

hand = 0
msg = 1


#construtor de um pacote
def buildPackage(packType, **kwargs):

    # Cria o Pacote nessa ordem: TIPO PACOTE, TAMANHO PAYLOAD, NUMERO DE PACOTES, ID PACOTE, EOP

    #Tipos:   Handshake - 0
    #         Mensagem Arquivo - 1
    #         Mensagem Número - 2

    # Cria uma lista com todos os packages:
    packageList = []
    if kwargs:
        content = kwargs.get('content', None)


    # Se o pacote for um handshake:
    if packType == 0:
        packTypeBytes = packType.to_bytes(2, byteorder = 'big')
        payloadSizeBytes = (0).to_bytes(2, byteorder = 'big')
        packNBytes = (1).to_bytes(2, byteorder = 'big')
        packIdBytes = (0).to_bytes(2, byteorder = 'big')
        eop = (1010).to_bytes(2, byteorder = 'big') #eop de um hanshake definido como 1010

        header = packTypeBytes + payloadSizeBytes + packNBytes + packIdBytes + eop
        eop = (1010).to_bytes(4, byteorder = 'big')
        pack = header + eop

        packageList.append(pack)
        return packageList
    
    # Se o pacote for uma mensagem(arquivo)
    elif packType == 1:
        payloadBuffer = open(content, 'rb').read()
        packN = math.ceil(len(payloadBuffer)/114) #dividir a imagem em pacotes de 114 bytes
        
        for packId in range(packN):
            if packId == packN-1:
                payloadSize = len(payloadBuffer) % 114
            else:
                payloadSize = 114
            packTypeBytes = packType.to_bytes(2, byteorder = 'big')
            payloadSizeBytes = payloadSize.to_bytes(2, byteorder = 'big')
            packNBytes = packN.to_bytes(2, byteorder = 'big')
            packIdBytes = packId.to_bytes(2, byteorder = 'big')
            eop = (2679).to_bytes(2, byteorder = 'big') #valor no eop de um pacote de arquivo          
            header = packTypeBytes + payloadSizeBytes + packNBytes + packIdBytes + eop

            payload = payloadBuffer[:payloadSize]
            payloadBuffer = payloadBuffer[payloadSize:] 
            eop = (2679).to_bytes(4, byteorder = 'big') 

            datagrama = header + payload + eop
            packageList.append(datagrama)
        return packageList
    
    #Teste: pacote 4 está listado como 1
    elif packType == 2:
        payloadBuffer = open(content, 'rb').read()
        packN = math.ceil(len(payloadBuffer)/114) #dividir a imagem em pacotes de 114 bytes
        
        for packId in range(packN):
            if packId == packN-1:
                payloadSize = len(payloadBuffer) % 114
            else:
                payloadSize = 114
            packTypeBytes = packType.to_bytes(2, byteorder = 'big')
            payloadSizeBytes = payloadSize.to_bytes(2, byteorder = 'big')
            packNBytes = packN.to_bytes(2, byteorder = 'big')
            if packId == 3:
                packId = 1
            packIdBytes = packId.to_bytes(2, byteorder = 'big')
            eop = (2679).to_bytes(2, byteorder = 'big') #valor no eop de um pacote de arquivo          
            header = packTypeBytes + payloadSizeBytes + packNBytes + packIdBytes + eop

            payload = payloadBuffer[:payloadSize]
            payloadBuffer = payloadBuffer[payloadSize:] 
            eop = (2679).to_bytes(4, byteorder = 'big') 

            datagrama = header + payload + eop
            packageList.append(datagrama)
        return packageList

    #Teste: tamanho do payload no head está incorreto
    elif packType == 3:
        payloadBuffer = open(content, 'rb').read()
        packN = math.ceil(len(payloadBuffer)/114) #dividir a imagem em pacotes de 114 bytes
        
        for packId in range(packN):
            if packId == packN-1:
                payloadSize = len(payloadBuffer) % 114
            else:
                payloadSize = 114
            packTypeBytes = packType.to_bytes(2, byteorder = 'big')
            payloadSizeBytes = (payloadSize).to_bytes(2, byteorder = 'big')
            if packId == 3:
                payloadSizeBytes = (payloadSize+20).to_bytes(2, byteorder = 'big')
            packNBytes = packN.to_bytes(2, byteorder = 'big')
            packIdBytes = packId.to_bytes(2, byteorder = 'big')
            eop = (2679).to_bytes(2, byteorder = 'big') #valor no eop de um pacote de arquivo          
            header = packTypeBytes + payloadSizeBytes + packNBytes + packIdBytes + eop

            payload = payloadBuffer[:payloadSize]
            payloadBuffer = payloadBuffer[payloadSize:]
                
            eop = (2679).to_bytes(4, byteorder = 'big') 

            datagrama = header + payload + eop
            packageList.append(datagrama)
        return packageList



def main():
    try:
        com1 = enlace('COM2') #Arduino 1 
        # com1 = enlace('COM2') #Virtual
        com1.enable()

        HEAD = 10
        EOP = 4

        serverResponseEmpty = True
        aliveCheck = True
        serverOk = False

        # -------------------------- HANDSHAKE --------------------------
        while aliveCheck:
            print("Checando status do server\n")
            hiMessage = buildPackage(hand)[0]
            com1.sendData(hiMessage)
            print("Esperando resposta do server\n")
            time.sleep(2)
            serverResponseEmpty = com1.rx.getIsEmpty()
            if serverResponseEmpty == True:
                retry = str(input("Servidor inativo. Tentar novamente? S/N: "))
                if retry == 'N' or retry == 'n':
                    aliveCheck = False
                    print("\nAbortando processo\n")
                    break
                else:
                    print("\nTentando novamente\n")
                    continue
            else:
                print("Servidor ativo\n-----------------------------------\n")
                aliveCheck = False
                serverOk = True
                time.sleep(2)

        # Só procede para o resto do código se o servidor estiver funcionando
        if serverOk:
            #Pede para o usuário selecionar uma imagem para ser transmitida
            print('\nPor favor escolha um arquivo:\n')
            Tk().withdraw()
            filename = askopenfilename()
            print("Arquivo selecionado: {}\n".format(filename))
            fileR = filename

            # -------------------------- TRANSMISSÃO DO DATAGRAMA + CONFIRMAÇÃO ------------------------
            # dataList = buildPackage(1, content = fileR)
            # Teste número errado
            # dataList = buildPackage(2, content = fileR)
            # Teste tamanho payload errado
            # dataList = buildPackage(3, content = fileR)
            for pack in dataList:
                packId = int.from_bytes(pack[6:8], byteorder='big') + 1
                packN = int.from_bytes(pack[4:6], byteorder='big')
                print("Mandando pacote {} de {}".format(packId, packN))
                com1.sendData(pack)
                time.sleep(1)
                print("Esperando confirmação")
                confirm, nRx = com1.getData(14)

    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
    except:
        print("ops! :-\\")
        com1.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
    