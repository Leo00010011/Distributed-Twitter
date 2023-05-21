### Client

|Protocolo|    Datos           |Destino    | Descripcion|
|---------|--------------------|-----------|------------|
|LOGIN_REQUEST    |Nick, Password      | EntryPoint| Petición del cliente para logearse           |
|REGISTER |Name, Nick, Password| EntryPoint| Petición del cliente para registrarse           |

### EntryPoint

|Protocolo  |    Datos           |Destino    | Descripcion|
|---------  |--------------------|-----------|------------|
|LOGIN_REQUEST      |Nick, Password, IDrequest      | Logger    | El entry point pide a un loguer que le resuelva el Token|
|LOGIN_RESPONSE      |Succesed, Token               | Client    | El entry point responde con el Token al cliente |
|NEW_LOGGUER_RESPONSE| IP| Logger | Respuesta al nuevo logger con el IP de algun logger para que coordinen|
|REGISTER   |Name, Nick, Password| Logger    |El entry point pide a un loguer que registre al usuario |
|ALIVE_REQUEST | | Logger | Pregunta a un Logger si est'a vivo |
|ALIVE_REQUEST | | DataBase | Pregunta a un Logger si est'a vivo |

### Loggers

|Protocolo    |    Datos           |Destino    | Descripcion|
|---------    |--------------------|-----------|------------|
|CHORD_REQUEST|Hash(Nick), IDrequest, IP| Logger| Busqueda con el algoritmo chord del Nodo del Usuario| 
|CHORD_RESPONSE | IP, IDrequest | Logger| Responde con el IP de la maquina con el recurso|
|LOGIN_REQUEST| IDrequest, Nick, Password| Logger |Pedir directamente el token|
|LOGIN_RESPONSE | Succesed, IDrequest, TOKEN     |Logguer| Encontrado el recurso del Chord, enviarselo al Logguer que lo solicitó|
|LOGIN_RESPONSE | Succesed, TOKEN, ID| EntryPoint | |
|NEW_LOGGER_REQUEST| IPorigin| EntryPoint|El nuevo logger pide IP de algun otro logger|
|ALIVE_RESPONSE | | EntryPoint | Avisa al EntryPoint que est'a vivo |
|REGISTERCHORD| Hash, Nick, Name, Password, IDClient, IPOriginNode |
|REGISTERERROR|
|GETTOKEN|Nick,,