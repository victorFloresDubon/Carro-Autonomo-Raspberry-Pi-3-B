# Carro Autónomo con Raspberry Pi 3 B+ y OpenCV

El proyecto está constituido por los archivos siguientes:

<code>servidor.py</code> este programa se ejecuta primero, ya que se hace uso de la librería OpenCV para el reconocimiento de imágenes de nuestro modelo ya entrenado con los clasificadores en cascada dentro la carpeta <code>cascade_xml</code>.

<code>carro_autónomo.py</code> este programa se ejecuta dentro de la Raspberry Pi 3 B+ el cual, es el que ejecuta el sensor ultrasónico, el control de los motores y la cámara. Y, este envía los datos por medio de socket para el programa servidor.

Asegúrate de tener la dirección IP del equipo donde ejecutarás el programa <code>servidor.py</code>.  Para ello es necesario modificar la variable <code>server_ip</code> dentro de ambos programas.

Si el servidor será la misma Raspberry Pi, se configurará de la siguiente forma:

```
server_ip = 'localhost'
```
## Diagrama en Fritzing
<img src="Diagrama\Carro autónomo_Raspberry_B+.png" alt="carro ensamblado"></img>

---
## Carro Ensamblado
<img src="Diagrama\20230609_134625.jpg" alt="carro ensamblado"></img>