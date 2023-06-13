export = WebsocketServer;
declare class WebsocketServer extends BaseServer {
  static heartbeatInterval: number;
  implementation: WebSocket.Server<WebSocket.WebSocket>;
}
declare namespace WebsocketServer {
  export { WebSocketServerConfiguration, ClientConnection };
}
import BaseServer = require("./BaseServer");
import WebSocket = require("ws");
type WebSocketServerConfiguration =
  import("../Server").WebSocketServerConfiguration;
type ClientConnection = import("../Server").ClientConnection;
