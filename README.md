# Remote_File_Server

This project creates a local file server: <br/>

## Getting Started

Use any python IDE to open the project. I personally use python IDLE.You can download python IDLE from the following links:
* [IDLE](https://www.python.org/downloads/) - Python IDLE

### Installation

- None

## Running the tests

- The description of each function will be located on top of them. Please read them before running to understand the overall structure of the project. <br/>
- To start the server and the client, open two terminals and go to "src" directory, and type the following comments for each terminals:

 **Server**
```
python server.py <port number> (ex: 9090)
```
![Server_Start](/images/server_starts.png)

- Before starting the server, please specify a Server_Directory in the main function. Otherwise, it will use the default Server Directory.
- For <port number>, select a port number that is not registered. An already registered or an invalid input will be detected and the program will not be executed.
- When the server starts, it will print out the host name, its IP Address, and the port number. Then it will inform the user that a socket is created with port specified above, and the server will continuously wait for requests from the clients.
  
**Client**  
```
python client.py <invocation semantics> (ex: "At-Most-Once" or "At-Least-Once")
```
![Client_Start](/images/client_starts.png)

- For <invocation semantics>, type "amo" for "At-Most-Once" and "alo" for "At-Least-Once".
- When client starts, under the welcome line, it asks the user to input the address of the host which can be found on the server side, the port number which should match the one for the server, and the amount of time in seconds a file or a content is able to stay in Cache.
- After all the inputs are specified, the terminal will show all the operations and their descriptions available for the user to request from the server. Some of the operations include Read, Write, Monitor, etc.
- At the bottom, the client will ask the user to input the request.
  
![Operations](/images/operations.png)

**Sending Request, Receiving Response**
- When the server receives the request and the corresponding parameters from the client, the server will analyze those request and parameters and decide whether or not the request will be successful. The server then sends the status of the request. It will either be "Success" or "Failed".

- The following are the terminal views when a successful request has been sent and returned.
![Server_Succ](/images/server_successful.png)
![Client_Succ](/images/client_successful.png)

- The following are the terminal views when an unsuccessful request has been sent and returned (Reading a text file that does not exist in the server directory).
![Server_Fail](/images/server_fail.png)
![Client_Fail](/images/client_fail.png)

- For more details, please download the code and try sending requests to the server.


## Deployment

Choose your own Server Directory & transfer files remotely.

## Built With

* [Python](https://www.python.org/) - The Programming Language

## Author

* **CSY** - [csy0522](https://github.com/csy0522)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
