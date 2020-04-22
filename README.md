# Remote_File_Server

This project creates a local file server: <br/>

## Getting Started

Use any python IDE to open the project. I personally use python IDLE.You can download python IDLE from the following links:
* [IDLE](https://www.python.org/downloads/) - Python IDLE

### Installation

...

## Running the tests

- The description of each function will be located on top of them. Please read them before running to understand the overall structure of the project. <br/>
- To start the server and the client, open two terminals and go to "src" directory, and type the following comments for each terminals:

 **Server**

```
python server.py <port number> (ex: 9090)
```
- For <port number>, select a port number that is not registered. An already registered or an invalid input will be detected and the program will not be executed.
- When the server starts, it will print out the host name, its IP Address, and the port number. Then it will inform the user that a socket is created with port specified above, and the server will continuously wait for requests from the clients.
  
**Client**  
```
python client.py <invocation semantics> (ex: "At-Most-Once" or "At-Least-Once")
```
- For <invocation semantics>, type "amo" for "At-Most-Once" and "alo" for "At-Least-Once".
- When client starts, under the welcome line, it asks the user to input the address of the host which can be found on the server side, the port number which should match the one for the server, and the amount of time a file or a content is able to stay in Cache.
- After all the inputs are specified, the terminal will show all the operations and their descriptions available for the user to request from the server.
- At the bottom, the client will ask the user to input the request.


## Deployment

Choose your own Server Directory & transfer files remotely.

## Built With

* [Python](https://www.python.org/) - The Programming Language
* [socket](https://docs.python.org/3/library/socket.html) - Python Module Providing Access To the BSD Socket Interface

## Author

* **CSY** - [csy0522](https://github.com/csy0522)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
