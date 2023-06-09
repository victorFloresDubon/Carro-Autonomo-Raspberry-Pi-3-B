"""
Universidad Mariano Galvez de Guatemala
Curso: Inteligencia Artificial

Proyecto: Carro Autónomo con Raspberry Pi

"""
import RPi.GPIO as GPIO
from io import BytesIO
from socket import socket, AF_INET, SOCK_STREAM
from picamera import PiCamera
from struct import pack
from threading import Thread
from time import  sleep, time

# Configuramos las GPIO de la Raspberry Pi en modo BCM
GPIO.setmode(GPIO.BCM)

# Configuramos los pines para el ultrasonico
TRIG = 18 # GPIO18 (Pin 12)
ECHO = 24 # GPIO24 (Pin 18)

# Configuramos los pines de los motores
ENA = 12 # GPIO12 (Pin 32)
IN1 = 5  # GPIO5  (Pin 29)
IN2 = 6  # GPIO6  (Pin 31)
ENB = 16 # GPIO16 (Pin 36)
IN3 = 13 # GPIO13 (Pin 33
IN4 = 19 # GPIO19 (Pin 35)

# Quitamos las advertencias GPIO
GPIO.setwarnings(False)

# Configuración de la PiCam
image_width = 640    # Ancho de la imágen
image_height = 480   # Altura de la imágen
image_fps = 10       # FPS
recording_time = 600 # Tiempo de grabación

# Configuración del sensor ultrasónico
ultrasonico_habilitado = True
# Configuración del sensor de los motores
motores_habilitado = True

# Configuración de puertos para envío de datos
#server_ip = 'localhost'
#server_ip = '192.168.0.2'
server_ip = '192.168.180.201'
log_habilitado = True
server_port_camera = 7690
server_port_mensaje = 7691
server_port_ultrasonico = 7692


# Clase para manejar los mensajes enviados por el servidor de OpenCV
class MensajeListener():
    
    def __init__(self, host, port):
        print( '?? init-mensajeListener' +  str( host ) + ':' + str( port ))
        self.host = host
        self.port = port
        # Conecta al socket
        #self.cliente = socket(AF_INET, SOCK_STREAM)
        #self.cliente.connect( (host, port) )
    
    """
    Examina los mensajes enviados por el servidor de acuerdo a lo observado por la cámara o
        el sensor ultrasónico
    """
    def get_mensaje(self):
        # Recibiremos un mensaje de 8 bytes de longitud
        cliente = socket(AF_INET, SOCK_STREAM)
        cliente.connect( (self.host, self.port) )
        mensaje = cliente.recv(1024)
        #mensaje = self.sock.recv(1024)
        #mensaje = mensaje.decode("utf-8")
        print(mensaje)
        print(f"Mensaje recibido {mensaje!r}")
        cliente.close()
        # Retornamos el mensaje decodificado
        return mensaje.decode()
    
# Esta clase permite controlar la transmisión de los motores
class TransmisionMotores():
    
    # Definimos la función que permitirá avanzar nuestros motores
    def avanzar(self):
        print("Avanzar") 
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
    # Definimos la función que permitirá retroceder nuestros motores
    def retroceder(self):
        print("Retroceder")    
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    # Definimos la función que permitirá girar a la izquierda
    def giro_izquierda(self):
        print("Giro Izq.")
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
    # Definimos la función que permitirá girar a la derecha    
    def giro_derecha(self):
        print("Giro Der.")    
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
    # Definimos la función que permitirá detener los motores
    def detener(self):
        print("Detener")        
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
    
    def __init__(self):
        print( '++ Iniciando control de movimiento ' )
        sleep(1.5)
        """
        Se estará utilizando una placa controladora L298N para el control de los motores.
        Dicha placa debe tener una entrada de voltaje de 12V o una batería de 9V; la salida GND de la placa controladora
        debe estar conectada a cualquier pin GND de la Raspberry Pi
        """
        # Configuramos los pines como salidas, los mismos están definidos anteriormente
        GPIO.setup(ENA, GPIO.OUT)
        GPIO.setup(ENB, GPIO.OUT)
        GPIO.setup(IN1, GPIO.OUT)
        GPIO.setup(IN2, GPIO.OUT)
        GPIO.setup(IN3, GPIO.OUT)
        GPIO.setup(IN4, GPIO.OUT)
        
        # Configuramos los pines ENA y ENB como salidas PWM
        PWM_ENA = GPIO.PWM(ENA, 1000)
        PWM_ENB = GPIO.PWM(ENB, 1000)
        # Luego, definimos su configuración a 50 Hz. para que tengan suficiente potencia
        PWM_ENA.start(75)
        PWM_ENB.start(75)
        try:
            ml = MensajeListener(server_ip, server_port_mensaje)
            print("+++ Esperando mensaje")
            print(ml.get_mensaje())
            
            while True:
                msg = ml.get_mensaje()
                if msg == 'F':
                    break
                # Avanzar
                elif msg == 'A':
                    self.avanzar()
                # Retroceder
                elif msg == 'R':
                    self.retroceder()
                # Detener
                elif msg == 'D':
                    self.detener()
                # Sin mensaje
                elif msg == '':
                    self.detener()
                
        finally:
            self.detener()
            print(' -- Motores detenidos')
            
# Esta clase se encarga del control del sensor ultrasónico
class TransmisionUltrasonico():
    
    def get_distancia(self):
        # Emitimos un pulso desde el TRIGGER para medir la distancia
        GPIO.output(TRIG, True)
        sleep(0.00001)
        GPIO.output(TRIG, False)
        
        inicio_pulso = time()
        # Obtenemos el tiempo de inicio del pulso mientras la entrada del ECHO es cero
        while GPIO.input(ECHO)==0:
            inicio_pulso = time()
        
        # Obtenemos el tiempo de finalización del pulso mientras la entrada del ECHO es uno
        while GPIO.input(ECHO)==1:
            fin_pulso = time()
        
        # Calculamos la diferencia entre el tiempo de inicio y finalización para obtener la duración
        duracion = fin_pulso - inicio_pulso
        # Calculamos la distancia obtenida multiplicando la duración por 17150
        distancia = duracion * 17150
        # Redondeamos a 2 decimales
        distancia = round(distancia, 2)
        return distancia
        
    def __init__(self):
        print( '+ Intentando conectar la transmisión del ultrasónico al servidor en ' + str( server_ip ) + ':' + str( server_port_ultrasonico ) )
        # Configuración de los pines del ultrasónico TRIGGER y ECHO
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)
        
        # Apagamos el trigger para que no emita señal a la primera
        GPIO.output(TRIG, False)
        
        # Creamos la conexión al host y enlazamos los puertos
        cliente_socket = socket(AF_INET, SOCK_STREAM)
        cliente_socket.connect( ( server_ip, server_port_ultrasonico ) )
        
        try:
            while True:
                # Obtenemos la medida
                distancia = self.get_distancia()
                # Si el log está habilitado imprimimos en consola la medida obtenida
                if log_habilitado:
                    print( "Distancia: %.1f cm" % distancia )
                # Enviamos el dato como cadena a través del puerto en codificación UTF-8
                cliente_socket.send( str( distancia ).encode('utf-8') )
                sleep(0.5)
        
        finally:
            print("Finalizando conexión con sensor ultrasónico")
            cliente_socket.close()
            #GPIO.cleanup()

# Esta clase permite controlar la transmisión de la PiCam
class TransmisionClienteCamara():
    
    def __init__(self):
        print( '+ Intentando conectar la transmisión de la cámara al servidor en ' + str( server_ip ) + ':' + str( server_port_camera ) )
        
        # Establecemos la conexión con los puertos y los enlazamos al cliente
        cliente_socket = socket(AF_INET, SOCK_STREAM)
        cliente_socket.connect((server_ip, server_port_camera))
        conexion = cliente_socket.makefile('wb')
        
        try:
            with PiCamera() as camara:
                # Definimos la resolución de la cámara
                camara.resolution = (image_width, image_height)
                # Definimos el ratio de marcos (FPS)
                camara.framerate = image_fps
                
                # Le damos 2 segundos a la cámara para iniciarse
                sleep(2)
                tiempo_inicio = time()
                transmision = BytesIO()
                
                # Enviamos la transmisión de video en formato JPEG
                for foo in camara.capture_continuous(transmision, 'jpeg', use_video_port=True):
                    conexion.write(pack('<L', transmision.tell()))
                    conexion.flush()
                    transmision.seek(0)
                    conexion.write(transmision.read())
                    if time() - tiempo_inicio > recording_time:
                        break
                    transmision.seek(0)
                    transmision.truncate()
            conexion.write(pack('<L', 0))                    
            
        finally:
            conexion.close()
            cliente_socket.close()
            print( 'Transmisión de la cámara, finalizada!' )
        
# Esta clase se encargará del control de los diferentes hilos para nuestro carro
class ThreadCliente():
    
    # Hilo del cliente de la PiCam
    def cliente_camara(host, puerto):
        print( '+ Iniciando la transmisión de la cámara en ' + str( host ) + ':' + str( puerto ) )
        TransmisionClienteCamara()
        
    # Hilo del cliente del sensor ultrasonico
    def cliente_ultrasonico(host, puerto):
        print( '+ Iniciando la transmisión del sensor hacia ' + str( host ) + ':' + str( puerto ) )
        TransmisionUltrasonico()

    # Hilo del cliente de los motores
    def cliente_motores(host, puerto):
        print( '+ Iniciando la transmisión de motores hacia ' + str( host ) + ':' + str( puerto ) )
        TransmisionMotores()
       
    print( '+ Iniciando logs del cliente - Logs ' + ( log_habilitado and 'activado' or 'desactivado'  ) )
    
    if ultrasonico_habilitado:
        thread_ultrasonico = Thread(name='thread_ultrasonico', target=cliente_ultrasonico, args= (server_ip, server_port_ultrasonico))
        thread_ultrasonico.start()

    if motores_habilitado:
        thread_motores = Thread(name='thread_motores', target=cliente_motores, args= (server_ip, server_port_mensaje))
        thread_motores.start()
        
    thread_camara = Thread(name='thread_camara', target=cliente_camara, args=(server_ip, server_port_camera))
    thread_camara.start()
    
if __name__ == '__main__':
    try:
        ThreadCliente()
    except KeyboardInterrupt:
        print("Cliente finalizado")
        GPIO.cleanup()
