import pexpect as proc
from pexpect import popen_spawn as spawn
import socket
import time
import sys
# Make python file(AI)
#P1 = spawn.PopenSpawn("python AI-dqn.py", logfile=sys.stdout)
#P2 = spawn.PopenSpawn("python fast_simulation.py", logfile=sys.stdout)
P1 = proc.spawn("python AI-dqn.py", logfile=sys.stdout)
P2 = proc.spawn("python fast_simulation.py", logfile = sys.stdout)
print("Waiting for import tensorflow...")
time.sleep(1)
Log = open("Log_Client_fast.txt", "w")
# Functions used to communicate with AI
def write_log(S):
    Log = open("Log_Client_fast.txt", "a")
    Log.write(S+"\n")
    Log.close()

def get_input(P, S):
    P.sendline(S)
    write_log("Sent Signal "+S)
    if P==P1: x=P.expect("C1")
    elif P==P2: x=P.expect("C2")
    if x==0:write_log("SUCCESS")
    #.expect(S)
    print(S)
    if P==P1: F = open("Msg1.txt", "r")
    elif P==P2: F = open("Msg2.txt", "r")
    #print(S)
    Msg = F.readline().rstrip('\n')
    F.close()
    if len(Msg)>10: write_log("Recieved message length of "+str(len(Msg)))
    else : write_log("Recieved message : " + Msg)
    return Msg

def print_out(P, Msg):
    if P==P1: F = open("MsgC1.txt", "w")
    if P==P2: F = open("MsgC2.txt", "w")
    F.write(Msg+"\n")
    F.close()
    if len(Msg)>10 : write_log("Sent message length of "+str(len(Msg)))
    else : write_log("Sent message : " + Msg)
    if P==P1: P.sendline("1X")
    if P==P2: P.sendline("2X")
    #P.sendline("CX")
    time.sleep(0.05)

step = 1
# Communication
while True:
    print("Step " + str(step))
    data = get_input(P2, "2X")
    print_out(P1, data)
    action = get_input(P1, "1X")
    print_out(P2, action)
    res = get_input(P2, "2X")
    print_out(P1, res)
    step = step + 1

conn.close()
