/* dir
0 : left, 1 : down, 2 : right, 3 : up
*/
import processing.net.*;
import java.io.*;
Client myClient;//ADDED
float ratio = 4;

int PORT;
float[][][][] sx, sy;

int nx = 2, ny = 2;
float l = 400 / (nx+ny);

int[] c_dx = {1, 0, -1, 0};
int[] c_dy = {0, 1, 0, -1};

int[] l_dx = {0, -1, 0, 1};
int[] l_dy = {1, 0, -1, 0};

int st1 = 0;
int [] st2 = {0, 0, 0, 0, 0, 0, 0, 0};
int[][][] pp = new int[nx][ny][4];

Cross[][] mycross = new Cross[5][5];
ArrayList<Car> Cars = new ArrayList<Car>();

int[][][][] p;
int num_frame = int(250/ratio), cur_frame = 0;//ADDED
int[][][][] waiting = new int[nx][ny][4][2];//ADDED
int[][][][] not_waiting = new int[nx][ny][4][2];//ADDED

String int_to_string(int value, int size)
{
  String S = str(value);
  int len_extra = size-S.length();
  String res = "";
  while((len_extra--)>0)res+="0";
  return res+S;
}

void send_data()
{
  String S = "";
  move();
  int i,j,k;
  for(i=0;i<nx;i++) for(j=0;j<ny;j++) for(k=0;k<4;k++){
    S+=int_to_string(waiting[i][j][k][0], 2);
    S+=int_to_string(waiting[i][j][k][1], 2);
    S+=int_to_string(not_waiting[i][j][k][0] + not_waiting[i][j][k][1], 2);
  }
  myClient.write(S);
  write_log("Data sent : " + S);
  delay(50);
}

void send_point(String S)
{
  myClient.write(S);
  write_log("Point " + S + " sent");
}

int input_left = 0;
String res="";

void setup()
{
  frameRate(60);
  try{
    FileWriter output = new FileWriter("Log_processing.txt");
    output.close();
  }
  catch(Exception e){
    e.printStackTrace();
  }
  BufferedReader reader = createReader("param.txt");
  String line;
  try{
    line = reader.readLine();
  }catch (IOException e) {
    e.printStackTrace();
    line = null;
  }
  PORT = int(line);
  //Server myServer = new Server(this, 10000);
  myClient = new Client(this, "127.0.0.1", PORT);
  
  size(2000, 2000);
  write_log(str(width)+" "+str(height));
  rectMode(CENTER);
  ellipseMode(CENTER);
 
  int i, j, k, m;
 
  for(i=0;i<nx;i++) for(j=0;j<ny;j++)
  {
    mycross[i][j] = new Cross(width/(nx*2) * (2*i+1), height/(ny*2) * (2*j+1));
    for(k=0;k<4;k++) pp[i][j][k] = 0;
  }
 
  sx = new float[nx][ny][4][2];
  sy = new float[nx][ny][4][2];
  for(j=0;j<ny;j++)
  {
    for(i=0;i<nx;i++)
    {
      for(k=0;k<4;k++)
      {
        for(m=0;m<2;m++)
        {
          if(k==0)
          {
            sx[i][j][k][m] = mycross[i][j].center_x - width/nx/2.0;
            sy[i][j][k][m] = mycross[i][j].center_y + l/4*(2*m+1);
          }
          if(k==1)
          {
            sx[i][j][k][m] = mycross[i][j].center_x - l/4*(2*m+1);
            sy[i][j][k][m] = mycross[i][j].center_y - height/ny/2.0;
          }
          if(k==2)
          {
            sx[i][j][k][m] = mycross[i][j].center_x + width/nx/2.0;
            sy[i][j][k][m] = mycross[i][j].center_y - l/4*(2*m+1);
          }
          if(k==3)
          {
            sx[i][j][k][m] = mycross[i][j].center_x + l/4*(2*m+1);
            sy[i][j][k][m] = mycross[i][j].center_y + height/ny/2.0;
          }
        }
      }
    }
  }
 
  p = new int[nx][ny][4][2];
  for(i=0;i<nx;i++) for(j=0;j<ny;j++) for(k=0;k<4;k++) for(m=0;m<2;m++) p[i][j][k][m] = 0;
  for(i=0;i<nx;i++)
  {
    p[i][0][1][0] = 25;
    p[i][0][1][1] = 25;
    p[i][ny-1][3][0] = 25;
    p[i][ny-1][3][1] = 25;
  }
  for(j=0;j<ny;j++)
  {
    p[0][j][0][0] = 25;
    p[0][j][0][1] = 25;
    p[nx-1][j][2][0] = 25;
    p[nx-1][j][2][1] = 25;
  }  
  while(true)draw2();
}

class Cross
{
  Light[] mylight = new Light[4];
  int center_x, center_y;
 
  Cross(int center_x, int center_y)
  {
    this.center_x = center_x;
    this.center_y = center_y;
      
    int i;
      
    for(i=0;i<4;i++)
    {
      // initialization of traffic lights ; odd num -> green, even num -> red
      
      mylight[i] = new Light(0, i, center_x, center_y);
    }
  }
}

class Light
{
  int lmod;  // light mode; red(0), go straight(1), left turn(2), both(3), yellow(9)
  int num;  // number of traffic light(0<=num<=7)
  float ry,yy,ly,gy;  // coordination of red light, left-turn light(center of traffic light), green light
  float trsx, trsy;  // coordination of crossroad
  float h = 2*l/5, w = 14*l/15;  // height, width of traffic light
 
  int dir;  // direction of traffic light
  int ldx, ldy;  // l_dx, l_dy
 
  Light(int lmod, int num, int cx, int cy)
  {
    this.lmod = lmod;
    this.num = num;
    this.dir = num;
    this.ldx = 0;
    this.ldy = 1;
      
    ry = 4*l/16;
    yy = 7*l/16;
    ly = 10*l/16;
    gy = 13*l/16;
      
    trsx = cx;
    trsy = cy;
  }
}


class Car
{
  float x, y, ang, v=ratio*6*l/200;  // x, y coordination, angle, velocity
  int crossnum;  // car number(group)
  int dir;  // car direction
  int mod;  // car mod; go straight(1)
  int xx, yy;
  int turn; // 1 : straight, 2 : left, 3 : right
  float w = l/6;  // body size
  boolean turning;
  int t;
  Car(float x, float y, int i, int j, int dir, int mod)
  {
    this.crossnum = nx*j + i;
    this.dir = dir;
    this.x = x;
    this.y = y;
    this.xx = i;  
    this.yy = j;
    this.dir = dir;
    this.mod = mod;
    if(this.mod == 0) this.turn = 2;
    else this.turn = 2 * (int)random(2) + 1;
    this.ang = PI/2 * dir;
    this.turning = false;
    this.t=0;
  }
 
  void go_straight()
  {
    x += v*c_dx[dir];
    y += v*c_dy[dir];
  }
 
  void turn(float cx,float cy, float ang)
  {
    float newx, newy;
    this.ang += ang;
    newx = (x-cx) * cos(ang) - (y-cy) * sin(ang);
    newy = (x-cx) * sin(ang) + (y-cy) * cos(ang);
    x = newx + cx; y = newy + cy;
  }
 
  void changenum(int n, int d)
  {
    crossnum = n;
    xx = n % nx;
    yy = n / ny;
    dir = d;
    this.ang = PI/2 * dir;
  }
 
  void whereami()
  {
    int ex = width/nx;
    int ey = height/ny;
    xx = (int)(x/ex);
    yy = (int)(y/ey);
    
    if(xx>=nx) xx--;
    if(yy>=ny) yy--;
    
    crossnum = nx*yy + xx;
  }
}

void generate(boolean gen)
{
  int r,t;
  int i, j, k, m;
  //t = millis();
  t = cur_frame;
  //if(t-st1 > 1000/ratio)
  if(ratio*(t-st1)>60)
  {
    //st1 = millis();
    st1 = cur_frame;
    for(j=0;j<ny;j++) for(i=0;i<nx;i++) for(k=0;k<4;k++) for(m=0;m<2;m++)
    {
      r = (int)random(100);
      if(gen)if(r<p[i][j][k][m]) Cars.add( new Car(sx[i][j][k][m], sy[i][j][k][m], i, j, k, m) );
      
      if(Cars.size()==0) continue;
      Car C = Cars.get( Cars.size()-1 );
      
      int crossnum = C.crossnum;
      int dir = C.dir;
      int mod = C.mod;
      float w = C.w;
        
      if(dir==0)
      {
        // prevent collision
        for(int q=Cars.size()-2;q>=0;q--)
        {
          Car K;
          K = Cars.get(q);
          if(K.crossnum==crossnum && K.dir == dir && K.mod == mod)
          {
            if(K.x - C.x < 1.5*w && K.x - C.x > 0)
            {
               Cars.remove(Cars.size()-1);
               break;
            }
            else break;
          }
        }
      }
      else if(dir==1)
      {
        for(int q=Cars.size()-2;q>=0;q--)
        {
          Car K;
          K = Cars.get(q);
          if(K.crossnum==crossnum && K.dir == dir && K.mod == mod)
          {
            if(K.y - C.y < 1.5*w && K.y - C.y > 0)
            {
               Cars.remove(Cars.size()-1);
               break;
            }
            else break;
          }
        }
      }
      else if(dir==2)
      {
        // prevent collision
        for(int q=Cars.size()-2;q>=0;q--)
        {
          Car K;
          K = Cars.get(q);
          if(K.crossnum==crossnum && K.dir == dir && K.mod == mod)
          {
            if(C.x - K.x < 1.5*w && C.x - K.x > 0)
            {
               Cars.remove(Cars.size()-1);
               break;
            }
            else break;
          }
        }
      }
      else if(dir==3)
      {
        for(int q=Cars.size()-2;q>=0;q--)
        {
          Car K;
          K = Cars.get(q);
          if(K.crossnum==crossnum && K.dir == dir && K.mod == mod)
          {
            if(C.y - K.y < 1.5*w && C.y - K.y > 0)
            {
               Cars.remove(Cars.size()-1);
               break;
            }
            else break;
          }
        }
      }
    }
  }
}

void delete()
{
  Car C;
 
  for(int i=Cars.size()-1;i>=0;i--)
  {
    C = Cars.get(i);
    if( C.x>width || C.x<0 || C.y>height || C.y<0 ) Cars.remove(i);
  }
}

void change()
{
  for(int i=0;i<Cars.size();i++)
  {  
    Car C;
    C = Cars.get(i);
    C.whereami();    
  }
}

void move()
{
  for(int i=0;i<nx;i++) for(int j=0;j<ny;j++) for(int k=0;k<4;k++) waiting[i][j][k][0] = waiting[i][j][k][1] = not_waiting[i][j][k][0] = not_waiting[i][j][k][1] = 0;
  for(int i=0;i<Cars.size();i++)
  {
    Car C = Cars.get(i);
    int crossnum = C.crossnum;
    int xx = C.xx;
    int yy = C.yy;
    int dir = C.dir;
    int mod = C.mod;
    int turn = C.turn, go;
    int lmod = mycross[xx][yy].mylight[dir].lmod;
    float w = C.w;
    boolean cancarmove = true;
      
    if(turn == 1){
      if(lmod == 1 || lmod == 3) go = 1; // straigt
      else go = 0; // stop
    }
    else if(turn == 2){
       if(lmod == 2 || lmod == 3) go = 2; // left
       else go = 0;
    }
    else{
       go = 3; // right
    }
    
    if(mycross[xx][yy].center_x - l <= C.x && C.x <= mycross[xx][yy].center_x + l && mycross[xx][yy].center_y - l <= C.y && C.y <= mycross[xx][yy].center_y + l)
    {
      C.t = 0;
      if(C.turning){
        if(turn == 2){
         if(dir == 0) C.turn(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y - l, -C.v/(5*l/4));
         else if(dir == 1) C.turn(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y - l, -C.v/(5*l/4));
         else if(dir == 2) C.turn(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y + l, -C.v/(5*l/4));
         else if(dir == 3) C.turn(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y + l, -C.v/(5*l/4));
        }
        else if(turn == 3){
         if(dir == 0) C.turn(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y + l, C.v/(l/4));
         else if(dir == 1) C.turn(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y - l, C.v/(l/4));
         else if(dir == 2) C.turn(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y - l, C.v/(l/4));
         else if(dir == 3) C.turn(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y + l, C.v/(l/4));
        }
        continue;
      }
      
      if(go == 2)
      {
         C.turning = true;
         if(dir == 0) C.turn(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y - l, -C.v/(5*l/4));
         else if(dir == 1) C.turn(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y - l, -C.v/(5*l/4));
         else if(dir == 2) C.turn(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y + l, -C.v/(5*l/4));
         else if(dir == 3) C.turn(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y + l, -C.v/(5*l/4));
      }
      else if(go == 3)
      {
         C.turning = true;
         if(dir == 0) C.turn(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y + l, C.v/(l/4));
         else if(dir == 1) C.turn(mycross[xx][yy].center_x - l, mycross[xx][yy].center_y - l, C.v/(l/4));
         else if(dir == 2) C.turn(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y - l, C.v/(l/4));
         else if(dir == 3) C.turn(mycross[xx][yy].center_x + l, mycross[xx][yy].center_y + l, C.v/(l/4));
      }
      
      if(!C.turning){
        C.go_straight();
      }
    }
    else{
      if(turn == 2 && C.turning == true)  // left-turn light
      {
        C.turning = false;
        if(dir==0) C.changenum(C.crossnum,3);
        else if(dir==1) C.changenum(C.crossnum,0);
        else if(dir==2) C.changenum(C.crossnum,1);
        else if(dir==3) C.changenum(C.crossnum,2);
      }
      else if(turn == 3 && C.turning == true)  // right-turn light
      {
        C.turning = false;
        if(dir==0) C.changenum(C.crossnum,1);
        else if(dir==1) C.changenum(C.crossnum,2);
        else if(dir==2) C.changenum(C.crossnum,3);
        else if(dir==3) C.changenum(C.crossnum,0);
      }
      
      if(go == 0)  // red or yellow light
      {
        if(dir==0)
        {
          if( C.x <= mycross[xx][yy].center_x - l - w && C.x >= mycross[xx][yy].center_x - l - w - C.v ) cancarmove = false;
        }
        else if(dir==1)
        {
          if( C.y <= mycross[xx][yy].center_y - l - w && C.y >= mycross[xx][yy].center_y - l - w - C.v ) cancarmove = false;
        }
        else if(dir==2)
        {
          if( C.x <= mycross[xx][yy].center_x + l + w && C.x >= mycross[xx][yy].center_x + l + w - C.v ) cancarmove = false;
        }
        else if(dir==3)
        {
          if( C.y <= mycross[xx][yy].center_y + l + w && C.y >= mycross[xx][yy].center_y + l + w - C.v ) cancarmove = false;
        }
      }
      
      if(dir==0)
      {
        // prevent collision
        for(int j=0;j<Cars.size();j++)
        {
          Car K;
          K = Cars.get(j);
          if(K.crossnum==crossnum && K.dir == dir && K.mod == mod)
          {
            if(K.x - C.x < 1.5*w && K.x - C.x > 0)
            {
               cancarmove=false;
               break;
            }
          }
        }
      }
      else if(dir==1)
      {
        for(int j=0;j<Cars.size();j++)
        {
          Car K;
          K = Cars.get(j);
          if(K.crossnum==crossnum && K.dir == dir && K.mod == mod)
          {
            if(K.y - C.y < 1.5*w && K.y - C.y > 0)
            {
               cancarmove=false;
               break;
            }
          }
        }
      }
      else if(dir==2)
      {
        // prevent collision
        for(int j=0;j<Cars.size();j++)
        {
          Car K;
          K = Cars.get(j);
          if(K.crossnum==crossnum && K.dir == dir && K.mod == mod)
          {
            if(C.x - K.x < 1.5*w && C.x - K.x > 0)
            {
               cancarmove=false;
               break;
            }
          }
        }
      }
      else if(dir==3)
      {
        for(int j=0;j<Cars.size();j++)
        {
          Car K;
          K = Cars.get(j);
          if(K.crossnum==crossnum && K.dir == dir && K.mod == mod)
          {
            if(C.y - K.y < 1.5*w && C.y - K.y > 0)
            {
               cancarmove=false;
               break;
            }
          }
        }
      }
      
      if(cancarmove){
        not_waiting[xx][yy][dir][mod] ++;
        C.t=0;
        C.go_straight();
      }
      else if(!C.turning){waiting[xx][yy][dir][mod] ++; C.t++;}
    }
  }
}

void write_log(String x)
{
  try{
    FileWriter output = new FileWriter("Log_processing.txt", true);
    output.write(x+"\n");
    output.close();
  }
  catch(Exception e){
    e.printStackTrace();
  }
}

float[] s_total_time = {0,0,0,0};
String buf="";

/*String receive(int size)
{
  write_log(buf);
  String res = buf;
  buf = "";
  while(res.length()<size){
    if(myClient.available()>0){
      String S = myClient.readString();
      res += S;
      write_log(res);
    }
  }
  if(res.length()>size){
    buf = res.substring(size, res.length());
    res = res.substring(0, size);
  }
  return res;
}*/

int chk = 0;

void draw2()
{
  if(cur_frame%num_frame==0 && chk==0){//ADDED
     input_left = 2;
     res="";
     chk=1;
  }
  if(cur_frame%num_frame==0 && chk==1&&input_left>0){
    if(myClient.available()>0){
      String S = myClient.readString();
      res += S;
      input_left -= S.length();
    }
    if(input_left==0){ 
      write_log("Signal "+ res + " received");
    }
    return;
  }
  if(cur_frame%num_frame==0 && chk==1){//ADDED
     send_data();
     myClient.write("PX");
     input_left = 16;
     res="";
     chk=2;
  }
  if(cur_frame%num_frame==0 && chk==2 && input_left>0){
    if(myClient.available()>0){
      String S = myClient.readString();
      res += S;
      input_left -= S.length();
    }
    if(input_left==0){
      light_change_string(res); 
      write_log("Data "+ res + " received");
    }
    return;
  }
  if(cur_frame%num_frame==0)chk=0;
  if((cur_frame+1)%num_frame==0 && chk==0){//ADDED
     input_left = 2;
     res="";
     chk=1;
  }
  if((cur_frame+1)%num_frame==0 && chk==1 &&input_left>0){
    if(myClient.available()>0){
      String S = myClient.readString();
      res += S;
      input_left -= S.length();
    }
    if(input_left==0){ 
      write_log("Signal2 "+ res + " received");
    }
    return;
  }
  if((cur_frame+1)%num_frame==0&&chk==1){//ADDED
    float[] total_time = {0,0,0,0};
    String S = "";
    write_log("Total number of cars : " + str(Cars.size()));
    for(int i=0;i<Cars.size();i++){
      Car C = Cars.get(i);
      float t = C.t;
      total_time[C.crossnum]+=(t*t);
    }
    for(int i=0;i<4;i++){
      if(total_time[i]>s_total_time[i])S+="0";
      else S+="1";
      //S+=int_to_string(int(total_time[i]/10000),5);
      s_total_time[i]=total_time[i];
    }
    send_point(S);
    chk=0;
  }
  cur_frame++;
  
  generate(true);
  delete();
  change();
  light_change();
  move();
}

void light_change()
{
  // changing traffic light
  int t,i,j,k;
  //t = millis();
  t = cur_frame;
  for(i=0;i<nx;i++) for(j=0;j<ny;j++) for(k=0;k<4;k++)
  {
    //if(mycross[i][j].mylight[k].lmod==9 && t - st2[i] > 1000/ratio)
    if(mycross[i][j].mylight[k].lmod==9 && ratio*(t - st2[i]) > 60)
    {
      mycross[i][j].mylight[k].lmod = pp[i][j][k];
      pp[i][j][k] = 9;
    }
  }
}

void light_change_string(String S)
{
  // changing traffic light
  int i,j,k,x;
  //t = millis();
  for(i=0;i<nx;i++) for(j=0;j<ny;j++) for(k=0;k<4;k++)
  {
    x = S.charAt((i*ny+j)*4+k)-'0';
    if(mycross[i][j].mylight[k].lmod != x)
    {
      mycross[i][j].mylight[k].lmod = 9;
      //st2[i] = millis();
      st2[i] = cur_frame;
      pp[i][j][k]=x;
    }
  }  
}

void dash_line(float sx, float sy, float ex, float ey)
{
  float draw_step = 20, no_step = 20, i, dx = (ex-sx), dy = (ey-sy), Sx, Sy, Ex, Ey;
  float step = draw_step + no_step;
  float l = sqrt(dx*dx+dy*dy);
  for(i=0;i<l/step;i++) {
    Sx = sx+(int)(step*i*dx/l);
    Sy = sy+(int)(step*i*dy/l);
    Ex = sx+(int)((step*i+draw_step)*dx/l);
    Ey = sy+(int)((step*i+draw_step)*dy/l);
    stroke(255);
    line(Sx,Sy,Ex,Ey);
  }
}