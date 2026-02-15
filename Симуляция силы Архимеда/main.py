from vpython import *
import math

print("Введите начальную высоту объекта (либо выше уровня воды, либо ниже)")
n=int(input())

#-------------------------------------------------
surface = box(pos=vec(0, 0, 0), size=vec(50, 0.1, 50), color=color.blue, texture=textures.rough, opacity=0.5)
depth = box(pos=vec(0, -10, 0), size=vec(50, 20, 50), color=color.blue, texture=textures.rough, opacity=0.4)
bottom = box(pos=vec(0, -20, 0), size=vec(50, 0.5, 50), color=color.yellow, texture=textures.gravel,opacity=0.4, shininess=0)
s = sphere(pos=vec(0, 0, 0), radius=2, color=color.red)
s.pos.y=n
ymax = 0
ymin = bottom.pos.y
yT = s.pos.y
g = 9.8
pV = 997
pT=500
v = 4/3*math.pi*s.radius**3
#-------------------------------------------------

def F(p, g, v):
    return p * g * v

def ResForce(v,p,r):
    return 0.47*p*v*v*(math.pi*r**2)/2

def Volume(h,r):
    return math.pi*h**2*(3*r-h)/3

def Vy(a,t):
    return a*t

def Sy(V,t):
    return V*t

def classic():
    N = 50 #кол-во шагов
    dt = 1 / N #шаг
    sk=0.0000000001
    for k in range(1000000*N):
        if (s.pos.y>=ymax+s.radius):
            a=(ResForce(sk,1.2754,s.radius)-F(pT,g,v))/(pT*v)
        else:
            if (s.pos.y>=-s.radius):
                a=(F(pV,g,Volume(s.radius-(s.pos.y),s.radius))-F(pT,g,v)-sk/math.fabs(sk)*ResForce(sk,997,s.radius))/(pT*v)
            else:
                a=(F(pV,g,v)-F(pT,g,v)-sk/math.fabs(sk)*ResForce(sk,997,s.radius))/(pT*v)
        sk+=Vy(a,dt)
        s.pos.y +=Sy(sk,dt)
        rate(100)

def euler():
    sk = 0.0000000000000000001
    N = 50
    dt = 1 / N
    for k in range(100*N):
        if s.pos.y<=ymin+s.radius-bottom.size.y:
            a=0
            sk=0
        else:
            if (s.pos.y>=ymax+s.radius):
                a=(ResForce(sk,1.2754,s.radius)-F(pT,g,v))/(pT*v)
            else:
                if (s.pos.y>=-s.radius):
                    a=(F(pV,g,Volume(s.radius-(s.pos.y),s.radius))-F(pT,g,v)-sk/math.fabs(sk)*ResForce(sk,997,s.radius))/(pT*v)
                else:
                    a=(F(pV,g,v)-F(pT,g,v)-sk/math.fabs(sk)*ResForce(sk,997,s.radius))/(pT*v)
        sk+=a*dt
        s.pos.y +=sk*dt
        rate(100)
        
def midpoint():
    sk = 0.0000000000000000001
    N = 50
    dt = 1 / N
    for k in range(100 * N):
        if s.pos.y <= ymin + s.radius - bottom.size.y:
            a = 0
            sk = 0
        else:
            if (s.pos.y >= ymax + s.radius):
                a = (ResForce(sk, 1.2754,s.radius) - F(pT, g, v)) / (pT * v)
            else:
                if (s.pos.y >= -s.radius):
                    a = (F(pV, g, Volume(s.radius - (s.pos.y),s.radius)) - F(pT, g, v) - sk / math.fabs(sk) * ResForce(
                        sk, 997,s.radius)) / (pT * v)
                else:
                    a = (F(pV, g, v) - F(pT, g, v) - sk / math.fabs(sk) * ResForce(sk, 997,s.radius)) / (pT * v)
        sk+=a*dt
        s.pos.y +=dt*(sk+dt/2*a)
        rate(100)

def sravn():
    s_eu = sphere(pos=vec(-10, 0, 0), radius=2, color=color.green)
    s_mp = sphere(pos=vec(10, 0, 0), radius=2, color=color.yellow)
    s_eu.pos.y = s_mp.pos.y = s.pos.y
    sk_eu=sk_mp=sk = 0.0000000000000000001
    N = 50
    dt = 1 / N
    for k in range(1000000 * N):
        if s.pos.y <= ymin + s.radius - bottom.size.y:
            a = 0
            sk = 0
        else:
            if (s.pos.y >= ymax + s.radius):
                a = (ResForce(sk, 1.2754, s.radius) - F(pT, g, v)) / (pT * v)
            else:
                if (s.pos.y >= -s.radius):
                    a = (F(pV, g, Volume(s.radius - (s.pos.y), s.radius)) - F(pT, g, v) - sk / math.fabs(sk) * ResForce(
                        sk, 997, s.radius)) / (pT * v)
                else:
                     a = (F(pV, g, v) - F(pT, g, v) - sk / math.fabs(sk) * ResForce(sk, 997, s.radius)) / (pT * v)
            sk += Vy(a, dt)
            s.pos.y += Sy(sk, dt)
            rate(100)

        if s_eu.pos.y <= ymin + s_eu.radius - bottom.size.y:
            a_eu = 0
            sk_eu = 0
        else:
            if (s_eu.pos.y >= ymax + s_eu.radius):
                 a_eu = (ResForce(sk_eu, 1.2754, s_eu.radius) - F(pT, g, v)) / (pT * v)
            else:
                if (s_eu.pos.y >= -s_eu.radius):
                    a_eu = (F(pV, g, Volume(s_eu.radius - (s_eu.pos.y), s_eu.radius)) - F(pT, g, v) - sk_eu / math.fabs(sk_eu) * ResForce(
                        sk_eu, 997, s_eu.radius)) / (pT * v)
                else:
                    a_eu = (F(pV, g, v) - F(pT, g, v) - sk_eu / math.fabs(sk_eu) * ResForce(sk_eu, 997, s_eu.radius)) / (pT * v)
            sk_eu += a_eu * dt
            s_eu.pos.y += sk_eu * dt
            rate(100)

        if s_mp.pos.y <= ymin + s_mp.radius - bottom.size.y:
            a_mp = 0
            sk_mp = 0
        else:
            if (s_mp.pos.y >= ymax + s_mp.radius):
                a_mp = (ResForce(sk_mp, 1.2754, s_mp.radius) - F(pT, g, v)) / (pT * v)
            else:
                if (s_mp.pos.y >= -s_mp.radius):
                    a_mp = (F(pV, g, Volume(s_mp.radius - (s_mp.pos.y), s_mp.radius)) - F(pT, g, v) - sk_mp / math.fabs(sk_mp) * ResForce(sk_mp, 997, s_mp.radius)) / (pT * v)
                else:
                    a_mp = (F(pV, g, v) - F(pT, g, v) - sk_mp / math.fabs(sk_mp) * ResForce(sk, 997, s_mp.radius)) / (pT * v)
            sk_mp += a_mp * dt
            s_mp.pos.y += dt * (sk_mp + dt / 2 * a_mp)
            rate(100)




#euler()
#midpoint()
# classic()
sravn()




