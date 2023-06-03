from API.logger_server import LoggerServer
import API.util as util

LoggerServer(util.PORT_GENERAL_LOGGER,10,10,5).start_server()