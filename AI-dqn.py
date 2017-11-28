import random
import tensorflow as tf
import numpy as np
step = 0
max_train = 10000
Log = open('Log_fast.txt', 'w')
Log.close()
Log = open('Log_loss.txt', 'w')
Log.close()
move_to_string=["0000","0002","2000","0200","0020","0010","0001","1000","0100","0030","0003","3000","0300","1010","0101","0202","2020"]
dropout = 1.
train_mem = []
point_mem = []
action_mem = []

def log_result(step, loss, acc):
    Log = open('Log_loss.txt', 'a')
    Log.write("Epoch "+str(step)+" - Loss : "+str(loss)+", Accuracy : "+str(acc)+"\n")

def write_log(S):
    Log = open('Log_fast.txt', 'a')
    Log.write(S+"\n")
    Log.close()

def get_signal():
    line = raw_input()
    while line!="CX" : line+=raw_input()

def print_out(S):
    get_signal()
    Msg = open("Msg.txt", "w")
    Msg.write(S+"\n")
    Msg.close()
    print("1X")

def move(x):
    S = ""
    for i in range(len(x)): S+=move_to_string[x[i]]
    write_log("Sent "+S+" at step " + str(step))
    print_out(S)

def get_input():
    get_signal()
    Msg = open("Msg.txt", "r")
    line = Msg.readline().rstrip("\n")
    if len(line)>10 : write_log("Received message length of " + str(len(line)))
    else : write_log("Received message : " + line)
    Msg.close()
    print("1O")
    return line

def get_point():
    line = get_input()
    S = ""
    point = []
    for i in range(4):
        t = float(line[1*i:1*(i+1)])
        if t==0: point.append(-1)
        elif t==1 : point.append(1)
        else:
            write_log("INVALID INPUT")
            return 0
        S += (str(int(point[i]))+ " ")
    write_log("Point "+S+"recieved")
    return point

def get_data():
    line = get_input()
    x = []
    for i in range(48):
        t = int(line[2*i:2*i+2])
        x.append(np.log(1+t))
    write_log("Data recieved")
    x = np.array(x)
    return x.reshape([-1,12])

def get_train(p):
    return train_mem[p], point_mem[p], action_mem[p]

def add_train(x, p, action, pos):
    if pos==-1:
        train_mem.append(x)
        point_mem.append(p)
        action_mem.append(action)
    else:
        train_mem[pos]=x
        point_mem[pos]=p
        action_mem[pos]=action

def lrelu(x, alpha = 0.2):
    return tf.nn.relu(x) - alpha*tf.nn.relu(-x)
    
dat = np.zeros((4,4*12))
keep_prob = tf.placeholder(tf.float32)

#####
x = tf.placeholder(tf.float32, [None, 12*4])

W1 = tf.Variable(tf.random_normal([12*4, 128]))
b1 = tf.Variable(tf.random_normal([128]))

W2 = tf.Variable(tf.random_normal([128, 128]))
b2 = tf.Variable(tf.random_normal([128]))

W3 = tf.Variable(tf.random_normal([128, 128]))
b3 = tf.Variable(tf.random_normal([128]))

Wout = tf.Variable(tf.random_normal([128, 17]))
bout = tf.Variable(tf.random_normal([17]))

hidden1 = lrelu(tf.matmul(x, W1) + b1)
hidden1 = tf.contrib.slim.batch_norm(hidden1)
hidden2 = lrelu(tf.matmul(hidden1, W2) + b2)
hidden2 = tf.contrib.slim.batch_norm(hidden2)
hidden2 = tf.nn.dropout(hidden2, keep_prob)
hidden3 = lrelu(tf.matmul(hidden2, W3) + b3)
hidden3 = tf.contrib.slim.batch_norm(hidden3)
hidden3 = tf.nn.dropout(hidden3, keep_prob)
y = tf.matmul(hidden3, Wout) + bout

ans = tf.placeholder(tf.float32, [None, 17])
err = tf.reduce_mean(tf.square(y-ans))
opt = tf.train.AdamOptimizer(0.001).minimize(err)
#choice = tf.argmax(y,1)

init = tf.global_variables_initializer()
saver = tf.train.Saver(max_to_keep=None)
prob = 1.

#for i in range(step/100):
    #prob = prob*0.99

with tf.Session() as sess :
    sess.run(init)
    #saver.restore(sess, "./model/model104000.ckpt")
    avg_loss = 0.
    avg_acc = 0.
    while True:
        step = step + 1
        if step%100==0 and prob>0.1:prob=prob-0.001
        if step%10000==0:saver.save(sess, "./model/model"+str(step)+".ckpt")
        dat_in = get_data()        
        for k in range(dat.shape[0]):
            for i in range(3):
                for j in range(12):dat[k][i*12+j]=dat[k][(i+1)*12+j]
        for k in range(dat.shape[0]):
            for i in range(12):dat[k][3*12+i]=dat_in[k][i]

        res = sess.run(y, feed_dict = {x:dat, keep_prob:1.})
        action = []
        for k in range(dat.shape[0]):
            r = random.random()
            if r>prob:
                p=-1
                v=-1000000
                for i in range(17):
                    if v < res[k][i]:
                        v = res[k][i]
                        p = i
                write_log("action "+str(k)+" greedy")
            else:
                write_log("action "+str(k)+" random")
                p = random.randrange(0,17)
            action.append(p)
        #action = []		
        #for i in range(2): action.append( random.randrange(0,len(move_to_string)))
        move(action)
        point = get_point()
        l = len(action)
        #print(l)
        points = np.array(point)
        points = points.reshape([-1,1])
        dat_train = dat
        #print(res)
        #print(points)
        print(action)
        res1 = []
        res2 = []
        sum_acc = 0.
        for i in range(l):
            res1.append(points[i][0])
            if points[i][0] == 1: sum_acc = sum_acc + 1
            res2.append(res[i][action[i]])
        avg_acc = avg_acc + (sum_acc/l)
        print(res1)
        print(res2)
        sum_loss = 0.
        for i in range(l):
            loss = (res2[i]-points[i][0])*(res2[i]-points[i][0])
            sum_loss = sum_loss + loss
        avg_loss = avg_loss + (sum_loss/l)
        print(sum_loss)
        #print(train_mem)
        write_log("Total loss : "+str(sum_loss))
        if step%50==0:
            log_result(step/50, avg_loss/50,(avg_acc/50)*100)
            avg_loss = 0.
            avg_acc = 0.
        if len(train_mem)==max_train:
            p = random.randrange(0, max_train)
            dat_training, point_training, action_training = get_train(p)
            result_train = []
            write_log("Trained data " + str(p))
            res = sess.run(y, feed_dict={x:dat_training, keep_prob:1.})
            for i in range(l):
                tmp = []
                for j in range(17):
                   if j != action_training[i]: tmp.append(res[i][j])
                   else: tmp.append(point_training[i][0])
                result_train.append(tmp)
            #print(res)
            #print(result_train)
            sess.run(opt, feed_dict={x:dat_training, ans:result_train, keep_prob:dropout})
            add_train(dat_train, points, action, p)
        else:
            add_train(dat_train, points, action, -1)
        saver.save(sess, "model.ckpt")
    print("Yeah!\n")

