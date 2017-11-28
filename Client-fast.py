import pexpect as proc
import socket
import time
import sys

argv = sys.argv
if len(argv)==2 : PORT = int(sys.argv[1])
else : PORT = 12345
F = open('param.txt', 'w')
F.write(str(PORT))
F.close()
# Make python file(AI)
P1 = proc.spawn("python AI-dqn.py", logfile=sys.stdout)
P2 = proc.spawn("processing-java --sketch=traffic_simulation_fast --run", logfile=None)
Log = open("Log_Client_fast.txt", "w")
# Functions used to communicate with AI
def write_log(S):
    Log = open("Log_Client_fast.txt", "a")
    Log.write(S+"\n")
    Log.close()

def get_input(P, S):
    P.sendline("CX")
    P.expect(S)
    F = open("Msg.txt", "r")
    Msg = F.readline().rstrip('\n')
    F.close()
    if len(Msg)>10: write_log("Recieved message length of "+str(len(Msg)))
    else : write_log("Recieved message : " + Msg)
    return Msg

def print_out(P, Msg):
    F = open("Msg.txt", "w")
    F.write(Msg+"\n")
    F.close()
    if len(Msg)>10 : write_log("Sent message length of "+str(len(Msg)))
    else : write_log("Sent message : " + Msg)
    P.sendline("CX")
    time.sleep(0.05)

# Connect with processing(Simulation)
HOST = ''    
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print(1)
conn, addr = s.accept()
print('Connected by', addr)
buf = ""
# Functions used to communicate with Simulation program
def input_socket(conn, size):
    global buf
    res = buf
    buf = ""
    while len(res)<size:
        S = conn.recv(1024)
        if len(S)>0: print(res)
        res += S
    if len(res)>size:
        print(res)
        buf += res[size:]
        res = res[0:size]
        print(buf, res)
    write_log("Recieved message from socket : " + res)
    return res

def input_data(conn, size):
    output_socket(conn, "0X")
    return input_socket(conn, size)

def output_socket(conn, Msg):
    write_log("Sent message to socket : " + Msg) 
    print(conn.send(Msg))

def output_data(conn, Msg):
    input_socket(conn, 2)
    output_socket(conn, Msg)

step = 1
# Communication
while True:
    print("Step " + str(step))
    data = input_data(conn, 96)
    print_out(P1, data)
    action = get_input(P1, "1X")
    output_data(conn, action)
    res = input_data(conn, 4)
    print_out(P1, res)
    step = step + 1

conn.close()
