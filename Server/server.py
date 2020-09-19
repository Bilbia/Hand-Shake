#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação Server
####################################################

from enlace import *
import time

def confirmBuilder(packIdCheck, eopCheck):
    packTypeBytes = (0).to_bytes(2, byteorder = 'big')
    payloadSizeBytes = (0).to_bytes(2, byteorder = 'big')
    packNBytes = (1).to_bytes(2, byteorder = 'big')
    packIdBytes = (0).to_bytes(2, byteorder = 'big')

    if packIdCheck == True:
        pck = 10
    else:
        pck = 20

    if eopCheck == True:
        eopC = 10
    else:
        eopC = 20

    eopMsg = int(str(pck) + str(eopC))    
    eop = eopMsg.to_bytes(2, byteorder = 'big')

    header = packTypeBytes + payloadSizeBytes + packNBytes + packIdBytes + eop
    eop = eopMsg.to_bytes(4, byteorder = 'big')
    pack = header + eop

    return pack

def main():
    try:
        com2 = enlace('COM3') #Arduino 2
        # com2 = enlace('COM3') #Virtual
        com2.enable() 

        HEAD = 10
        EOP = 4

        #Manda mensagem para ver se está vivo
        print("Esperando mensagem de confirmação\n")
        hiHead, nRx = com2.getData(HEAD)
        hiEOP, nRx = com2.getData(EOP)
        packType = int.from_bytes(hiHead[:2], byteorder='big')
        eopCheck = int.from_bytes(hiHead[-2:], byteorder='big')
        eop = int.from_bytes(hiEOP, byteorder='big')
        
        if packType == 0 and eopCheck == eop: # Checa se o pacote é um Handshake e se o EOP condiz com o que o Header fala
            if eop == 1010:
                print("Conexão confirmada\n-------------------------\n")
                com2.sendData(hiHead + hiEOP)

        get = True
        packIdCounter = 0
        lista_payload = []
        print("Esperando pacotes\n-------------------------\n")
        while get:
            
            header, nRx = com2.getData(10)
            print("Recebendo Header...\n")
            time.sleep(0.5)
            plSize = int.from_bytes(header[2:4], byteorder='big')
            packN = int.from_bytes(header[4:6], byteorder='big')
            packId = int.from_bytes(header[6:8], byteorder='big')
            if packId != packN - 1:
                print("O tamanho do pacote está errado")
                plSize = 114
            print("Recebendo Payload...\n")
            payload, nRx = com2.getData(plSize)
            time.sleep(0.5)
            print("Recebendo EOP...\n")
            EOP, nRx = com2.getData(4)
            time.sleep(0.5)
            packIdCheck = True
            eopCheck = True

            
            eop = int.from_bytes(EOP, byteorder='big')
            eopHead = int.from_bytes(header[-2:], byteorder='big')
            print("Pacote {} de {} recebido\n".format(packId + 1, packN))
            print("Tamanho do pacote: {}\n".format(plSize))\

            if packId != 0:
                if packId != packIdCounter + 1:
                    packIdCheck = False
                    print("O pacote {} está fora de ordem\n".format(packId))
                else:
                    print("Ordem dos pacotes correta até agora\n")
            else: 
                print("Ordem dos pacotes correta até agora\n")
            
            print(eop)
            print(eopHead)
            if eop != eopHead:
                eopCheck = False
                print("EOP do pacote {} está incorreto\n".format(packId))
                print("Quantidade de bytes recebidos incompleta\n")

            if packId != 0:
                packIdCounter += 1
            lista_payload.append(payload)
            
            print("Mandando confirmação para o Client\n-------------------------\n")
            confirmMsg = confirmBuilder(packIdCheck, eopCheck)
            com2.sendData(confirmMsg)
            time.sleep(0.1)

        

            if packId == (packN-1):
                get = False

        print(lista_payload)
        imageW = "../imgs/recebidaCopia.png"
        image = b''.join(lista_payload)  
        f = open(imageW, 'wb')
        f.write(image)
        f.close()


        

        

        # Encerra comunicação
        print("-------------------------\n")
        print("Comunicação encerrada\nTransmissão bem sucedida\n")
        print("-------------------------\n")
        com2.disable()  
    except:
        print("ops! :-\\")
        com2.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
