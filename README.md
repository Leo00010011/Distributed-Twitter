# <center>Tweeter Distribuído 📱</center>

## Equipo:
- Lázaro Daniel González Martínez
- Alejandra Monzón Peña
- Leonardo Ulloa Ferrer

## Funcionalidades del Sistema

Dweeter (Distributed Tweeter), es una red social que permite a los usuarios compartir textos en sus perfiles y otra operaciones similares a las que se pueden realizar en la bien conocida aplicación de Tweeter. 

Las acciones que pueden realizar los usuarios son: 

>- Registrarse en el sistema
>- Iniciar Sesión
>- Publicar un Dweet
>- Re-publicar un Dweet
>- Seguir a otro usuario
>- Ver el perfil de algún usuario
>- Pedir nuevos Dweets
>- Cerrar sesión

#### Registrarse en el sistema 

Para registrarse el usuario debe proveer un `Nombre`, un `Nick` que ha de ser único y por el que se le identificará por los restantes usuarios para poder seguirlo y ver su perfil, y una `Contraseña`. 

La acción de un usuario de registrarse será exitosa si el `Nick` que escoja no está en uso, en caso contrario recibirá un mensaje informándole que debe buscar otro Nick.

#### Iniciar Sesión 
La acción de iniciar sesión requiere que el usuario esté registrado en el sistema. Para loggearse el usuario debe poner su `Nick` y `Contraseña`, si los datos son introducidos correctamente el loggeo será exitoso, en caso que la contraseña no se corresponda con el Nick o que el Nick no esté registrado se informará al usuario con un mensaje de combinación de Nick/Contraseña incorrecta.

Para poder publicar, seguir, re-publicar, ver perfiles y pedir visualizar Dweets el usuario debe estar loggeado en el sistema.

#### Publicar Dweet 
Publicar un Dweet requiere que el usuario introduzca el texto de la publicación, el cual no debe exceder los 225 caracteres.

Si el usuario está loggeado y el Dweet cumple las restricciones de tamaño, entonces se publicará el Dweet y este se agregará a su perfil.

#### Re-publicar un Dweet 
La acción de re-publicar un Dweet requiere que el usuario seleccione un Dweet existente, cuando esté viendo las publicaciones de otros usuarios si desea que esta se agregue a su perfil y que sea vista por sus seguidores puede optar por hacer un Re-Dweet.

#### Seguir un usuario

Un usuario para seguir a otro debe conocer su `Nick` y decir que quiere comenzar a seguir a ese usuario, si el Nick del usuario al que quiere seguir existe, comenzará a seguir a este usuario. Seguir a un usuario implica que cuando se pida ver nuevos Dweets las publicaciones y re-publicaciones de este usuario van a eventualmente aparecer, manteniéndose al tanto de su contenido.

#### Ver perfil
Para ver un perfil se debe introducir el `Nick` del usuario cuyo perfil se desea ver, esto mostrará todos los Dweets y ReDweets hechos por este usuario. 

#### Pedir nuevos Dweets
Esta acción muestra un conjuto de Dweets y ReDweets de usuarios a los que estás siguiendo, es una acción que mientras mas veces se repita más cantidad de contenido se podrá visualizar e se informará de publicaciones que aún no se hayan visto.

#### Cerrar Sesión 

Es la forma segura de salir de la red social y que nadie pueda acceder a tu cuenta a menos que conozca el `Nick` y `Contraseña` correspondientes para loggearse nuevamente.

### Interacción con Dwitter

El usuario para poder realizar todas las acciones disponibles utilizará una consola interactiva de apariencia sencilla y fácil uso.

## Almacenamiento de información

Para almacenar la información se utilizó una base de datos relacional en SQLite, el diseño de la misma y las operaciones de inserción, consulta, eliminación de datos se manejó con la librería `Peewee` de `Python`, que funciona muy similar a la ORM de Django.

### Almacenamiento distribuído

Como los servidores de datos (`TweeterServers`) están dispuestos en forma de anillo y se comunican para buscar los recursos mediante una `DHT` con un algoritmo `Chord`, entonces se aprovecha el identificador de cada Nodo del Chord para repartir la información a almacenar. Como en el algoritmo Chord cada Nodo responde por los recursos que tengan identificador menor que el de dicho Nodo y mayor que el de su antecesor en la DHT, y aprovechando las características propias de las Redes Sociales, en que todo requiere de un usuario registrado para poder intercambiar, utilizamos la misma función de `hash` con la que se decidió el identificador del Nodo para hashear los Nicks de los usuarios, de modo que todos los recursos (publicaciones, Nicks de a quienes sigue, Datos de loggeo, etc) relativos a usuarios con identificador en el mismo segmento del chord se encuentran en un mismo Nodo; mientras que usuarios con identifiador en dos secciones diferentes del anillo del chord tienen sus datos almacenados en Nodos diferentes. 

Con esta forma de distribuir los datos, mientras más crezca el número de usuarios de Dweeter, mayor cantidad de Nicks de usuario existirán y más equilibrada estará la cantidad de información almacenada en cada uno de los Nodos.

## Componentes y arquitectura de la Red

En el sistema distribuído Dweeter, exiten 4 componentes principales, cada una con un comportamiento y funcionalidades específicas en la red.

>-  Client
>-  EntryServer
>-  ChordServer
>-  TweeterServer

Cada computadora de la red tiene alguno de estos comportamientos asignados y en base a esto se establecen los protocolos de comunicación entre ellos para el manejo de datos.

Para `EntryServer`, `ChordServer` y `TweeterServer`, los cuales son realmente los servidores fundamentales de la red, se tiene que para reponder a peticiones utilizan una piscina de hilos, es decir tienen el comportamiento de un `MultiThreadedServer`, el cual describiremos detalladamente en próximas secciones.

A continuación explicamos con mayor detalle las funcionalidades y comportamiento de cada componente.


#### Client

Ofrece la funcionalidades para establecer la comunicación con los servicios generales del Dweeter, desde la perspectiva del cliente o consumidor. Es la componente más cercana al usuario.


#### EntryServer

Es la componente intermedia entre `Client`, `ChordServer`, y `TweeterServer`. Se encarga de recepcionar las peticiones del `Client`, reconocerlas, validarlas y hacer la petición al `TweeterServer`. Sirve para velar en parte por la seguridad del Sistema, al obligar la comuniación `Client-EntryServer` y `EntryServer-TweeterServer`, lo implica que el `Client` aunque quiera comunicarse con el `EntryServer` no podría hacerlo, o al menos no de forma trivial. Por otra parte al servir de mediadora, está capacitada para percibir cuándo hay un fallo en la red y notificar al `Client`. Además la interacción con `ChordServer` es la mínima necesaria para introducirlo al anillo del Chord, aclarando que realmente NO es el `EntryServer` quien decide dónde va el nuevo `ChordServer` en el anillo, sino que a este se le da el "contacto" de algún otro `ChordServer` ya insertado, y haciendo el algoritmo de Chord, este se podrá ubicar correctaemnte y hacer las transferencias de informacion que les sean necesarias.

#### ChordServer

Este tipo servidor se encarga de hacer funcionar el anillo del Chord, para poder buscar los datos distribuidos en el Sistema. Son las compoentes que más interacción tienen con los `TweeterServer` ya que estos estarán constantemente preguntándoles donde almacenar o extraer determinado registro de un dato. Estos son los que poseen la finger table, y la actualizan constantemente. Más adelante se exlicará a mayor profundidad el funcionamiento de los elementos internos de esta componente.

#### TweeterServer
Este servidor es el encargado de trabajar con la base de datos y buscar que todo lo pedido por el usuario sea consistente:

- Que el usuario esté loggeado en las acciones que lo requieran
- Que al usuario al que quieran seguir exista
- Que el Dweet que quieran ReDweetear exista
- Que al momento de loggearse sea correcta la información de Nick y Contraseña
- Que al registrarse el Nick de usuario sea único

Además de guardar en la base de datos los Dweets y ReDweets, nuevos Usuarios, Tokens de usuarios Loggeados, etc. 

Para el manejo de la base de datos utiliza las funciones existentes en el arcivo `view.py`.

Este Servidor se comunica con otros de su mismo tipo con el objetivo de:
>- Pedir información sobre la existencia de ciertos datos.
>- Pedirles que guarden datos que les pertenecen.
>- Replicar datos entre los servers dentro de un Nodo.
>- Informar de su llegada al sistema y traspasar datos cuando se agrega un nuevo Nodo.

La comunicación entre un TweeterServer y un ChordServer se emplea solamente para dos procesos:

>- Cuando la computadora se agrega al sistema y como ChordServer y TweeterServer coexisten en una misma máquina, atendiendo a peticiones por puertos diferentes, una vez que el ChordServer inserta la computadora en el Nodo correspondiente se informa a sí mismo, por el puerto del TweeterServer la información necesaria para que este pueda obtener los datos del Nodo al que pertenece. 
>- Cuando un TweeterServer necesita contactar con otro, que tiene los datos de un ususario en específico; para esto se comunica con el ChordServer desde el otro puerto de la misma computadora y le solicita que haga la búsqueda en la DHT para conseguirle los IPs de los servidores del Nodo con el que desea contactar.

Con el otro servidor que interactuan los TweeterServer es el EntryServer, el cual es el mediador entre los clientes y los TweeterServer.

>- Los TweeterServer se comunican con los EntryServer para responder a los mensajes de estos informándoles que aún están activos en la red.
>- Cuando un usuario quiere realizar cualquier acción en Dweeter, el EntryServer con el que conecte es el que se comunica con el TweeterServer y así se maneja la transacción de forma transparente para el usuario.

![](img.png)

# Mecanismos Preliminares Implementados

## Multithreaded server
La atencion a los clientes de cada uno de nuestros servicios tiene en común que siempre están esperando conexiones por un puerto determinado y cuando alguien se conecta se le destina un hilo de ejecución para atenderlo. Nosotros aprovechamos esta situación encapsulando este comportamiento en la clase MultiThreadedServer. Para especificar el comportamiento del servicio, cuando se construye el objeto se especifica el número de hilos, el puerto por donde se va a estar escuchando y se le pasa un delegado el cual va a ser el que debe responder al cliente.Este delegado recibe el socket y será ejecutado en su propio hilo. De esta forma logramos abstraer al que vaya a desarrollar un servicio de temas de escucha y threading.

Para nuestros servicios optamos que los clientes sean atendidos en hilos separados y no en procesos separados. La principal motivación de esto fue por las facilidades que estos permiten para la comunicación. Como se verá más adelante nuestros hilos aprovechan las características de su modelo de memoria para actualizar y leer constantemente objetos compartidos, este comportamiento sería mucho más costoso de imitar si hubiéramos optado por hacerlo con multiprocesos. A pesar de estas bondades, usar hilos en Python trae sus desventajas, como el hecho de que la concurrencia se ejecuta en un mismo procesador que hace que no se aproveche del todo el paralelismo.

Tener objetos compartidos lleva consigo el riesgo de la ocurrencia de complejos e impredecibles errores de sincronización, por lo que usamos varios mecanismos para evitarlos. La base de la mayoría de los mecanismos de sincronización es el semáforo el cual consiste en un entero y dos operaciones llamemoslas `release` y `acquire`. Si el entero es mayor que 0 la función acquire solo decrementa su valor, pero si el entero es cero, el llamado de esta función provoca que se detenga la ejecución del hilo que lo llamó. La función release incrementa el valor del entero del semáforo, y si el valor de este antes de ser incrementado era 0 entonces desbloquea a un hilo aleatorio de los que habían sido bloqueados por llamar su `acquire`. 

Usando esta idea tan sencilla se pueden implementar los candados, los cuales son semáforos en los que el entero puede ser solo `0` o `1`. Con candados se puede lograr el comportamiento de que los hilos accedan los objetos solo uno a la vez. Esto se hace creando un candado para ese objeto y haciendo que todo el que lo vaya a modificar llame `acquire` antes de hacerlo y `release` al haber terminado. Python tiene una implementación built-in de un candado (`Lock`).

Crear hilos tiene un costo, por lo que normalmente se opta por reutilzarlos. Para lograr esto utilizamos una estructura que se llama **multiconsumer**, **multiproducer queue**. Esta consiste en una cola con capacidad limitada que además de ser thread safe tiene la propiedad de que si se pide un elemento y la cola está vacía bloquea el hilo de ejecución de quien se lo pidió y al igual que cuando se va a insertar un elemento y está llena. Este comportamiento se puede lograr con dos semaforos, llamémosle **P** y **C**. Al comienzo el entero correspondiente a **P** comienza con el valor de la capacidad y el entero de **C** empieza con `0`. Cuando se añade un elemento a la cola se llama un `acquire` de **P** y un `release` de **C**, y cuando se saca un elemento se llama un `acquire` de **C** y un `release` en **P**. De esta forma se logra que el entero de **P** sea distinto de `0` ssi aún hay capacidad para más elementos y el entero de **C** es distinto de `0` ssi aún quedan elementos por consumir. Luego se puede construir la piscina de threads haciendo que todos los hilos que queremos utilizar estén en un ciclo pidiendo elementos a una cola como estas.

Teniendo en cuenta esto decidimos que el comportamiento del servidor se centre en una **multiproducer, multiconsumer queue**. Vamos a tener un hilo que se dedique a ,constantemente, aceptar conexiones y meter los socket en la cola. Por otro lado vamos a tener `n` hilos constantemente pidiéndole `sockets` a la cola para pasárselo a la función que proporcionó quien construyó el server. Cuando se termine la ejecución de esta función se va a volver a pedir un socket a la cola.

También con este server proveemos una funcionalidad para terminar de forma segura el servicio. Para esto utilizamos un objeto de `Python` llamado `Event` que entre otras funcionalidades puede servir como una variable booleana y que se puede modificar siendo thread safe. Lo otro que hay que tener en cuenta es que con la cola que usamos tiene la función de especificar el tiempo que se quiere esperar cuando se pide un elemento y esta está vacía. Con estas ideas lo que hicimos fue crear un `Event` y pasarle una referencia a todos los hilos, tanto el que está esperando conexiones como los que están consumiendo de la cola. Luego los hilos que consumen sale de su espera cada cierto tiempo y si la cola está vacía y el evento que se le pasó está seteado, salen del ciclo y retornan. De esta forma se asegura que el servidor no termine si tiene aún clientes por atender. El hilo que está aceptando conexiones puede usar una idea parecida pero este está bloqueado por la función `accept`. Para hacer salir un hilo de un `accept` hay varias ideas, como mandar una señal a uno mismo. La solución por la que optamos utiliza la función `wait` del Event, que en semejanza al candado bloquea el hilo de ejecución hasta que alguien llama a la función `set` de ese mismo evento. Lo que hicimos fue poner un hilo cuya única función es llamar al wait del event que se le pasó a todos los hilos y cuando salga de su espera lo primero que hace es mandar un mensaje vacío al localhost, esto desbloquea el `accept` y permite terminar el hilo que estaba escuchando.

## ThreadHolder y State Storage

Nosotros realizamos dos tipos de peticiones, unas que son respondidas inmediatamente, utilizando el mismo socket con el que se mandó la petición, y otras que pueden demorar y que pueden llegar desde cualquier servidor. Para implementar las segundas necesitabamos una forma de hacer que el hilo espere hasta que llegue la respuesta para él, pues en un momento determinado puede haber más de un hilo esperando por respuestas de este tipo. Esto lo resolvimos asignándole un `id` a cada hilo que esté esperando por respuesta y haciendo que este espere por un evento creado solo para él. De esta forma se puede enviar la petición con el `id` que se le asignó al hilo para que cuando llegue la respuesta esta pueda especificar el `id` del hilo que debe recibirla. Este comportamiento lo encapsulamos en las clases `ThreadHolder` y `StateStorage`. `ThreadHolder` sería el objeto que contiene el `id`, el evento y la variable a la que se le debe asignar la referencia a la respuesta. `StateStorage` es el objeto que se encarga de coordinar todos los `ThreadHolder`. Entre sus funciones principales está poder retribuir un `ThreadHolder` dado su `id`, y poder crear nuevos `ThreadHolders` asignándole un `id` distinto a los del resto. Usando estos objetos se puede realizar las peticiones que necesitabamos con solo pedir un nuevo `ThreadHolder` al `StateStorage`, enviar la petición con el `id` del `ThreadHolder` y esperar al evento que contiene también este objeto. De esta forma cuando llegue la respuesta con el id, se le puede pedir al StateStorage el `ThreadHolder` con este `id`, copiar la referencia a la respuesta en su variable y activar el evento al que estaba esperando el hilo. 

## Chord DHT

Por motivos de escalabilidad la base de datos de nuestro proyecto debe estar distribuida en varios servidores. Para poder trabajar de esta forma necesitamos una forma de encontrar el servidor que contiene la sección de la base de datos que puede responder a nuestras queries. Una solución a este problema es implementar una **Distributed Hash Table** (`DHT`). 

En nuestro caso nos basamos en **Chord** que es un tipo de DHT. Su idea se basa en asignarle un id a cada servidor y organizarlos en forma de anillo, ordenados en sentido de las manecillas del reloj. Luego, asumiendo que cada dato tiene una llave numérica, este va a estar almacenado en la sección de la base de datos del servidor que cumple que su `id` es mayor o igual a la llave del dato y el de su antecesor es menor estricto, a partir de ahora esto va ser equivalente a decir que ese servidor es sucesor de esa llave. El nodo de menor `id` es un caso especial pues su antecesor es el máximo y siempre es mayor que él. Por esto decidimos que al mínimo pertenece el dato cuyo `id` es menor que el del mínimo o mayor que el del  máximo.

Por motivos también de escalabilidad un nodo de Chord no debe tener que estar al tanto de la existencia de todos los nodos que participan en la `DHT`. Si cada nodo conociese el id y la direccion IP de su sucesor y su predecesor entonces cualquier nodo pudiera resolver quién tiene cierto dato recorriendo el anillo. Pero esta estrategia es bastante lenta considerando que probabilísticamente la mitad de las peticiones tendrían que ser redirigidas a través de la mitad del anillo para ser resueltas.

Existe una forma de hacerlo con un mejor equilibrio entre nodos que necesita conocer un nodo y redirecciones por las que necesita pasar una petición. Se puede almacenar tantos nodos como  parte entera por debajo del logaritmo en base 2 del mayor `id` posible y que estos cumplan que el `i`-ésimo sea el sucesor de id $+ 2^{i - 1}$. A la tabla con estos nodos se le conoce como Finger Table y ahora la petición en vez de redirigirsela al sucesor, se redirige al nodo con mayor `id` que sea menor que la llave del dato. Solo se le redirige la petición a alguien con `id` mayor cuando es el sucesor, que en este caso se habría encontrado a quien posee el dato. Esta forma de buscar es correcta porque siempre avanza y a alguien que es menor que la llave al no ser que esté seguro de que posea el dato y se mantiene la propiedad de que solo necesita que el sucesor y el predecesor estén correctos para que la búsqueda correctamente.

Nuestra DHT está pensada para ser construida de manera incremental. Para insertar un nuevo nodo `N` solo se necesita que el nodo que va a ser el predecesor de N lo ponga como su sucesor en la finger table y que el nodo que va a ser su sucesor ponga a N como su predecesor. Cuando se crea el nodo se le asigna un ID, en nuestro caso el `SHA256` de su propio IP. Luego, asumiendo que la `DHT` está funcionando correctamente, se le pregunta a un nodo cualquiera por el servidor que es sucesor del ID que se le asignó a `N`. Como el predecesor de este sucesor es también el predecesor del nuevo nodo todo el proceso de inserción ocurre entre estos tres. El nuevo nodo le avisa a su sucesor que él es su nuevo predecesor, a lo que este le responde con el `id` y el IP de su predecesor. Luego le dice al predecesor que él es su nuevo sucesor, haciendo que este modifique su **finger table**. Para terminar se le vuelve a escribir al sucesor para confirmar que ya el predecesor lo tiene como sucesor haciendo que este lo ponga como su predecesor en su figer table. Las finger table del resto de los nodos está en un estado que permite que las búsquedas funcionen bien porque como se hizo notar antes esto solo depende de que el predecesor y el sucesor estén correctos, y los que debían cambiar ya fueron cambiados. Pero se necesita que el nuevo nodo se tenga en cuenta en las finger table del resto para que las redirecciones sean más eficientes, por lo que cada nodo actualiza su tabla periódicamente preguntando por el sucesor del valor correspondiente a cada fila. Como esta búsqueda funciona correctamente, las filas de las finger table a las que le corresponda el nuevo nodo van a ser corregidas eventualmente.

Lo que hemos mostrado hasta ahora explica el funcionamiento de la mayoría de los casos. Pero como un nodo puede resolver quién posee un dato con una llave menor que la de él y su predecesor. Todo nodo tiene conocimiento de su predecesor inmediato y se podría recorrer,pero esto implicaría una busqueda lineal. Otra alternativa es redirigir la petición al mínimo pues si la llave sigue siendo menor que él, es de él y si es mayor con las finger table se puede buscar eficientemente. Pero hacer que todos los nodos lleven la cuenta de quién es el mínimo en este momento tiene sus complicaciones, pues en este caso sería otro factor que influye en la correctitud. La alternativa que encontramos es hacer que todos los nodos respondan por su `id` y por `id` $+$ `MAX`, donde `MAX` es el mayor `id` posible. De esta forma por ejemplo el sucesor inmediato del máximo es el mínimo pero con el `id` + `MAX`. Ahora cuando un nodo quiera encontrar a alguien que tiene un `id` menor que él solo tiene que preguntar por el sucesor de la llave del dato sumado a `MAX`.

# Comunicación de Componentes


Para la comunicación entre las componentes del sistema se creó un protocolo de comunicación. Cada mensaje enviado en la red tiene la estructura [ Tipo | Protocolo | Datos ], de modo que cada Server pueda distinguir basándose en el `Tipo` del Server que le escibe y en el `Protocolo` del mensaje, cuáles son las acciones a realizar y cuales son los valores que están almacendaos en los `Datos`. 

Los tipos disponibles son: `Client, Entry, Logger, Tweet, Chord`

uno por cada Servidor que interviene,excepto los TweeterServer que por cuestión de comodidad responden tanto como tipo Logger como por tipo Tweet, para separar las funcionalidades de registro y loggeo del resto de manejo de Dweets y ReDweets.


## Consultas

El mecanismo base para hacer una consulta completa desde el cliente pasa por una serie de pasos:

- El `Client` realiza la petición con un `EntryServer`, y mantiene la comunicación abierta hasta que se le responda.
- El `EntryServer` le escribe a algún `TweeterServer` con la solicitud de la consulta que desea realizar, y cierra la conexión.
- El `TweeterServer` le pide a su `ChordServer` correspondiente el ip del `TweeterServer` que debe tener la información solicitda y cierra la conexión.
- Los `ChordServer` realizan la búsqueda con el algoritmo de Chord y al encontrar al indicado, se le escribe nuevamente al `TweeterServer` inicial, con el IP del servidor que puede responder la consulta, y se cierra la conexión.
- Este `TweeterServer` le escribe al que tiene los datos que necesita, haciendo al solicitud, y cierra la conexión.
- Al realizar la consulta, se le responde abriendo una nueva conexión.
- Luego el `TweeterServer` inicial le responde por una nueva conexión, al `EntryServer` con los datos solicitados.
- Y finalmente el `Client` recibe la respuesta de la consulta.

Debemos aclarar algunas cosas de este proceso. La comunicación entre componentes NO `Client`, tiene sentido que se hagan abriendo y cerrando una conexión para preguntar, y hacer lo mismo para responder. Por qué? Pues, es un puerto menos utilizado que estará esperando una respuesta; al realizar la búsqueda con el Chord se formaría un arco de conexiones abiertas, que deberían esperar una respuesta por la misma conexión, y esto obligaría a dejar las conexiones mucho más tiempo abiertas, y en el caso de que una de estas intermedias se rompiera, la respuesta final no llegaría al `TweetServer`; y además hay consultas donde el `TweetServer` necesita hacer varias peticiones en vez de una sola. Por otra parte la conexión entre `Client` y `EntryServer` tiene sentido dejarla abierta ya que el Server no tendría forma de comunicarse con el cliente abriendo una nueva conexión, ya que para hacer esto, los `Client` deberían entonces tambíen estar escuchando por un puerto continuamente, y esta función la consideramos innecesaria de momento.

Cosas importantes a tener en cuenta, es que cuando se realiza una consulta, tanto el `EntryServer` como el `TweeterServer` esperan un tiempo de seguridadpara recibir la respuesta, y si no la reciben antes de este tiempo, notifican un error. De esta manera se garantiza que los hilos con los que se realizan las peticiones no queden flotando e inutilizándose.

## Stalking

Este proceso consiste en "preguntar continuamente" a otra componente si está disponible en la red. La utiliza principalmente el `EntryServer`, para reconocer a los otros `EntryServer`y los `ChordServer` que están vivos. El funcionamiento es bastante sencillo:

> Cada cierto tiempo aleatorio (con probabilidad uniforme) el `EntryServer` manda un mensaje con protocolo `ALIVE_REQUEST` a estos sevidores, esperando una respuesta, la cual de ser recibida, se actualiza el último tiempo de vida de dicha componente. En caso que no se reciba respuesta, este tiempo de vida no se actualiza, y poco tiempo después, por lo general, luego de 3 veces sin tener contacto con la componente, se considerará "muerta".

Considerar una componente "muerta" tiene una interpretación diferente para cada tipo de componente.

- En el caso de que un `ChordServer` se considere muerto por un `EntryPoint`, implica que cuando otro `ChordServer` se quiera introducir al anillo del Chord, el `EntryPoint` NO le recomendará el IP del `ChordServer` muerto, sino aleatoriamente otros que estén vivos. Además como en la implementación del Sistema, los Servidores `TweeterServer` y `ChordServer` se montan sobre la misma PC, sirve también para no incluir una componente `TweeterServer` caída, al solicitar servicios generales entrantes del `Client`, como iniciar sesión, ver perfil, etc...
- En el caso de que un `EntryPoint` sea el muerto, entonces se añade a la `Lista de Tareas` de este (luego se verá mejor), enviar los IPs de los `ChordServer` que el vivo tiene, una vez que el `EntryPoint` muerto reaparezca.

Note que el principal beneficio de este proceso de `Stalking` es que se evita los fallos producidos cuando una PC sale del Sistema. Pero en contraposición se genera conexiones extras en el red, lo cual podríamos pensar que recargaría esta; sin embargo note que al acosar a una componente se hace en luego de un tiempo random, lo cual posibilita que la red realmente no se sobrecargue, al menos en la mayoría del tiempo.

## Tareas Pendientes

Este proceso consiste en disponer de una lista de acciones que la componente actual debe realizar con otra componente, y debido a algún motivo no pudo hacerla en un comienzo pero tiene la necesidad de hacerla en algún momento. Además como parte de este proceso, está el hecho de enviar estas tareas. Por lo general quienes utilizan una lista de tareas pendientes son el `EntryServer` y el `TweetServer`.

En sí el proceso consite un poco más a detalle en:
> Llevar un diccionario con los IPs de las componentes a las que posiblemente se les podría enviar una acción retrasada, y su lista de acciones retrasadas. Cada cierto tiempo aleatorio (probabilidad uniforme) se envían las tareas retrasadas. Si estas llegan correctamente, se van eliminando del diccionario.

El tipo de tarea pendiente varía según la componente que emite la acción:

- En el caso de los `EntryServer`, las tareas pendientes, van más relacionadas con agregar un `TweeterServer` que se insertó en el anillo del Chord, para notificar al resto de `EntryServer`, que hay un nuevo IP válido de `TweeterServer` y/o `ChordServer` al que se le puede hacer alguna petición. Algo importante, es que 

- En el caso de los `TweeterServer` sus tareas pendientes son internas con las réplicas dentro del Nodo. En este caso cuando un `TweeterServer` agregue una info nueva, está se añadirá a sus tareas pendientes, y luego de un rato, se enviará al destinatario final.

Note que la lista de tareas de esta forma eventualmente actualizará a las componentes finales. En cuanto a la sobrecarga que pueda provocar en la red es similar a  la del `Stalking`, donde las peticiones no se realizan todas a la vez, sino entre tiempos aleatorios.

## Inserción de un nuevo `ChordServer-TweeterServer`

Cuando un nuevo `ChordServer-TweeterServer` se quiere insertar en el anillo del Chord, primero estable una comunicación con algún `EntryServer` para pedir algún `ChordServer` que ya esté en el anillo del Chord. Luego le pide a este le pide el ip del servidor que es sucesor del id que se le asignó. Luego este le avisa al sucesor que es su nuevo predecesor y al predecesor de su sucesor que es su nuevo sucesor, quedando insertado en sus fingertable, y por supuesto construye la suya con este sucesor y el otro predecesor. Finalmente cuando el Chord se inserta se comunica con el `EntryServer` para notificarle que se insertó correctamente, al igual que se comunica con su `TweeterServer` asociado para indicarle el id que le corresponde, sus sucesores, y sus hermanos.

## Réplicas y Transferencia de Datos

Cuando un nuevo `TweeterServer-ChordServer` se inserta al anillo del Chord este en un inicio debe saber cómo quiere insertarse, si como nuevo Nodo, o como réplica en otro nodo. En cualquiera de ambos casos por lo general ocurríra una trnasferencia de muchos datos, ya que:

- En el caso de insertarse como nuevo nodo, deberá copiar los datos que le corresponden en su rango de hash asignado.
- En el caso de insertarse como réplica dentro de un nodo, deberá replicar todos los datos que tenga el nodo.

Por este motivo, una vez insertado al anillo, la parte `ChordServer` le informa a la `TweeterServer` de ese ordenador mediante un mensaje con los datos `chord_id`, `succesors` y `siblings`, que son el identificador que tienen dentro del anillo, una lista con los IPs de sus sucesores en el anillo y una lista con los IPs de las otras máquinas de su propio Nodo(hermanos), respectivamente, esta última será vacía en el caso que sea el primero de ese Nodo. Basándose en esta información, el `TweeterServer` establecerá comunicación con alguno de sus hermanos en caso de tener, o con alguno de sus sucesores en caso contrario, creando un nuevo hilo para dicha comunicación.


Para realizar una transferencia de datos correcta, el orden en que se transfieran las tablas de la base de datos importa, debido a que los usuarios sun llaves foráneas en la mayoría de la tablas, la tabla de ususarios ha de ser la primera en copiarse. De este modo se van transfiriendo bloques de datos entre una computadora y la otra hasta que se hayan enviado toda la base de datos.

>Para la transferencia de datos se requiere que el servidor nuevo envíe su `chord_id` para que así el otro servidor sepa que porción de la base de datos enviar. 
Los datos se transfieren en bloques de 20 filas de la tabla cada vez.

# Tolerancia a Fallas

Un sistema distribuido por lo general puede presentar 3 tipos de fallas: las transitorias, las permanentes, y las intermitentes. A continuación explicamos las tolerancias con las que cuenta nuestro sistema distribuído:

- Lectura correcta de mensajes: Todo información que se envíe debe respectar el protocolo de comunicación explicado. Si por alguna extraña razón los bytes transferidos se modificaran y llegaran con algún defecto, los componentes al recibirlos e intentar decodificarlos, lo notarán y lo descartarán notificando por lo general un error en la conexión. Esto nos ayudará a que una falla intermitente de eeste estilo, mate hilos de ejecución.

- Envío Múltiple: En la mayoría de las comunicaciones las componentes implicadas en el envío de información contarán con una pequeña lista de IPs a los que pudiera solicitar la consulta. Entonces en vez de establecer la comunicación solamente con una componente, esta intentará establecer una conexión con cada uno, y con el primero que esta conexión se establezca, se realizará la consulta. Es importante aclarar que NO es que se intenten abrir de forma simultánea todas estas conexiones sino que se van probando uno a una, hasta que la primera acierte. Note que esto disfraza algunas las fallas transitorias cuando no se puede establecer conexión con alguna componente, y el cliente por otra parte no se entera con cuantos servidores no se pudo estableceruna comunicación.

- Envío persistente: Hay casos donde es necesario establecer una comunicación con una componente específica y que aún cuando no esté disponible, se le envíe al reincorporarse al sistema. Ejemplo de ello son las `Tareas Pendientes`. En sentido general tenemos 2 categorías para esta tolerancia:
    - Relajado: Es cuando el recurso o el mensaje que se quiere enviar no requiere de una prioridad sumamente alta, y por lo tanto se intenta reenviar luego de un tiempo no tan corto (generalmente aleatorio). Dígase por ejemplo, datos que debe actualizar una réplica; en este caso, es necesario que la réplica en cuestión agregue esa información, pero por lo general si esta conexión no se establece es porque dicha réplica está caída, así que debe tomar su tiempo reincorporarla, por lo tanto no hay necesidad de insistir con una frecuencia muy alta. Y de esta forma se van realizando otras tareas que sí se pueden realizar.
    - Frencuente: Es cuando el recurso o el mensaje que se quiere enviar tiene un alto grado de prioridad, por ejemplo la actualización de la DHT del anillo del Chord. El único factor del que depende el funcionamiento correcto de Chord es que el sucesor y el predecesor puestos en la finger table estén correctos. Por lo que al insertarse un nodo en el Chord este lo intenta persistentemente, pues de quedarse a medias el proceso el predecesor de su sucesor y el sucesor de su predecesor puede quedar en un estado incorrecto.

    De esta manera note que los fallos temporales al sacar alguna réplica del Sistema, y luego integrarlas se evitarían.

- Réplica de información en un nodo: Relacionado con el punto anterior, si ocurre un fallo permanente donde una réplica sale del Sistema, digamos que porque dicha PC se rompió, se le quemaron los discos, etc, pudiera reemplzarse por otra, que al añadirla nuevamente al nodo obtendría toda la información que se había perdido, ya que dentro de un nodo se replica la información. De esta manera note que el usuario no se entera cuándo desapareció una réplica por este causa, y tampoco cuándo se incorpora una nueva.

- Sugerencia de Componentes Vivas: Ya explicamos en secciones anteriores cómo funciona el proceso de `Stalking`, pero debemos señalar que este tiene un papel importante para evitar fallas transitorias de errores en la red para comunicarse con alguna componente, pues cuando un `ChordServer` le pide a un `EntryPoint` algún IP de alguien en el anillo, para poder incorporarse, este le da aleatoriamente una lista pequeña de `ChordServer`s que fueron acosador recientemente y se suponen que estén vivos. De esa forma es más probable que se logre establecer una conexión.

- Tiempo de Espera: Cuando se hace una petición entre componentes cuya respuesta no será inmediata, por lo general se toma un tiempo para procesar la consulta entera. Además habrá veces donde luego de hacer alguna petición se pudiera romper la conexión antes de recibir una respuesta. Por lo tanto una forma de evitar provocar un error mayor, como dejar trabajando un hilo innecesariamente o incluso que pueda quedarse siempre flotando inutilizado, es esperar un tiempo la respuesta de la consulta. Si la respuesta llega a tiempo, el flujo de la operación que se esté realizando continúa, pero en caso de que el tiempo de espere se sobrepase, se para la operación y se notifica que se agotó el tiempo de espera. De cara al cliente esto es de lo único que se puede enterar para peticiones que vengan desde el `Client`, pero ni tan siquiera sabrá si fue que una réplica se cayó, u otra cosa. En dicho caso, el usuario podría repetir la consulta.

## Transparencia de las operaciones

Cuando un cliente accede a cualquiera de las funcionalidades de Dweeter, todas las acciones que el sistema realice se mantienen transparentes para él. La única información que conoce un usuario es que se está comunicando con un servidor al que le está haciendo peticiones y que este le envía respuestas, pero jamás contacta siquiera con los `ChordServer-TweeterServer`, ni conoce que su información está fragmentada en distintas computadoras de la red. 

## Caché del Cliente

Además de todas las funcionalidades que brinda el Sistema Distribuido se implementó del lado del `Cliente` un `ShellCLient` interactivo para que el usuario pueda estar dentro de `Dweeter`. Esta implementación además cuenta con una memoria `Caché` de la información de perfiles. Esta se va llenando a medidad que se van visitando perfiles, o pidiendo nuevos Dweet y/o ReDweets; y finalmente cuando no haya conexión se le mostrará al usuario publicaciones guardadas en ellas. De esta forma el usuario puede entretenerse con publicaciones que aunque ya las vio, puede analizarlas mejor y no tener una pantalla en blanco, mientras regresa la conexión.