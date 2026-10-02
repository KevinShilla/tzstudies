"""Create clearly labelled mathematical plots and diagrams for worked keys."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc, Wedge
import numpy as np

DEST=Path(__file__).resolve().parents[1]/'answer_keys'/'figures'
DEST.mkdir(parents=True,exist_ok=True)
BLUE='#1a5276'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False})

def finish(fig,name):
    fig.savefig(DEST/name,dpi=220,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def building(name,height=37.3046,base=80,angle=25):
    fig,ax=plt.subplots(figsize=(6.8,3.4))
    ax.plot([0,base,base,0],[0,0,height,0],color=BLUE,lw=2)
    ax.plot([base-3,base-3,base],[0,3,3],color=BLUE)
    ax.add_patch(Arc((0,0),24,24,theta1=0,theta2=angle,color=BLUE))
    ax.text(13,3,f'{angle}°',color=BLUE)
    ax.text(base/2,-6,f'{base} m',ha='center')
    ax.text(base+3,height/2,'h',va='center')
    ax.text(base+3,height,'Top',va='center')
    ax.text(0,-6,'Observer',ha='center')
    ax.set_aspect('equal');ax.axis('off');ax.set_xlim(-10,base+18);ax.set_ylim(-12,height+8)
    finish(fig,name)

def frequency(name,x,y,xlabel='Age (years)',ylabel='Frequency (students)'):
    fig,ax=plt.subplots(figsize=(6.8,3.8))
    ax.plot(x,y,'o-',color=BLUE,lw=2,markersize=5)
    ax.set_xticks(x);ax.set_yticks(range(0,int(max(y))+2))
    ax.set_xlabel(xlabel);ax.set_ylabel(ylabel);ax.set_ylim(0,max(y)+1)
    ax.grid(alpha=.22);fig.tight_layout();finish(fig,name)

def circle_parts(name):
    fig,ax=plt.subplots(figsize=(5,4.5))
    A=np.array([np.cos(np.radians(30)),np.sin(np.radians(30))])
    B=np.array([np.cos(np.radians(100)),np.sin(np.radians(100))])
    C=np.array([np.cos(np.radians(200)),np.sin(np.radians(200))])
    D=np.array([np.cos(np.radians(300)),np.sin(np.radians(300))])
    ax.add_patch(Wedge((0,0),1,30,100,color='#edf4f8'))
    ax.add_patch(Circle((0,0),1,fill=False,color=BLUE,lw=1.7))
    ax.add_patch(Arc((0,0),2,2,theta1=30,theta2=100,color='#267144',lw=4))
    ax.plot([A[0],0,B[0]],[A[1],0,B[1]],color=BLUE,lw=1.5)
    ax.plot([C[0],D[0]],[C[1],D[1]],color=BLUE,lw=1.7)
    for label,p in zip('ABCD',[A,B,C,D]):ax.text(p[0]*1.13,p[1]*1.13,label,ha='center',va='center')
    ax.text(0,-.08,'O',ha='center');ax.text(.30,.48,'Sector\nAOB',ha='center',fontsize=10)
    ax.text(.93,.26,'Radius AO',fontsize=10,ha='left');ax.text(.34,1.06,'Arc AB',fontsize=10)
    ax.text(-.25,-.74,'Chord CD',ha='center',fontsize=10)
    ax.set_aspect('equal');ax.set_xlim(-1.25,1.65);ax.set_ylim(-1.2,1.25);ax.axis('off')
    finish(fig,name)

if __name__=='__main__':
    building('BasicMath-F2-2021-building.png')
    building('BasicMath-F2-2023-building.png')
    frequency('BasicMath-F2-2021-frequency.png',[12,13,14,15,16,17,18,19],[0,2,3,5,6,3,1,0])
    circle_parts('BasicMath-F2-2022-circle.png')
    fig,ax=plt.subplots(figsize=(6,3.4))
    ax.plot([0,5,5,0,0],[0,0,2,2,0],color=BLUE,lw=2)
    ax.text(2.5,-.3,'5 cm',ha='center');ax.text(5.15,1,'2 cm',va='center')
    ax.text(2.5,1,'Scale 1:100',ha='center')
    ax.set_aspect('equal');ax.set_xlim(-.5,6);ax.set_ylim(-.6,2.5);ax.axis('off')
    finish(fig,'BasicMath-F2-2022-scale.png')
    fig,ax=plt.subplots(figsize=(6,3.4))
    ax.add_patch(Circle((-.65,0),1.2,fill=False,color=BLUE,lw=1.7));ax.add_patch(Circle((.65,0),1.2,fill=False,color=BLUE,lw=1.7))
    ax.text(-1.1,0,'500',ha='center');ax.text(0,0,'100',ha='center');ax.text(1.1,0,'600',ha='center')
    ax.text(-1,1.45,'Goats',ha='center');ax.text(1,1.45,'Cows',ha='center')
    ax.text(2,-1.2,'Neither: 300',ha='center')
    ax.set_aspect('equal');ax.set_xlim(-2.1,2.8);ax.set_ylim(-1.6,1.8);ax.axis('off')
    finish(fig,'BasicMath-F2-2022-venn.png')
    height=(4**2-3.5**2)**.5
    fig,ax=plt.subplots(figsize=(5.5,3.4))
    ax.plot([0,7,3.5,0],[0,0,height,0],color=BLUE,lw=2)
    ax.text(3.5,-.35,'7 cm',ha='center');ax.text(1.25,height/2+.25,'4 cm',ha='center');ax.text(5.7,height/2+.25,'4 cm',ha='center')
    ax.set_aspect('equal');ax.set_xlim(-.5,7.5);ax.set_ylim(-.7,height+.6);ax.axis('off')
    finish(fig,'BasicMath-F2-2024-isosceles.png')
    fig,ax=plt.subplots(figsize=(5.5,3.4))
    ax.plot([0,12,12,0],[0,0,5,0],color=BLUE,lw=2)
    ax.plot([11.6,11.6,12],[0,.4,.4],color=BLUE)
    ax.text(6,-.55,'12 m',ha='center');ax.text(12.3,2.5,'5 m',va='center')
    ax.text(5,3.3,'Ladder: 13 m',rotation=22,ha='center')
    ax.set_aspect('equal');ax.set_xlim(-.5,14);ax.set_ylim(-1,6);ax.axis('off')
    finish(fig,'BasicMath-F2-2025-ladder.png')
    fig,ax=plt.subplots(figsize=(6,3.4))
    ax.add_patch(Circle((-.65,0),1.2,fill=False,color=BLUE,lw=1.7));ax.add_patch(Circle((.65,0),1.2,fill=False,color=BLUE,lw=1.7))
    ax.text(-1.1,0,'20',ha='center');ax.text(0,0,'10',ha='center');ax.text(1.1,0,'10',ha='center')
    ax.text(-1,1.45,'Chemistry',ha='center');ax.text(1,1.45,'Physics',ha='center');ax.text(2,-1.2,'Neither: 5',ha='center')
    ax.set_aspect('equal');ax.set_xlim(-2.1,2.8);ax.set_ylim(-1.6,1.8);ax.axis('off')
    finish(fig,'BasicMath-F4-2021-venn.png')
    fig,ax=plt.subplots(figsize=(8,4.5))
    level_nodes={0:[('',0)],1:[('G',1.9),('N',-1.9)],2:[('GG',2.8),('GN',1),('NG',-1),('NN',-2.8)],3:[('GGG',3.2),('GGN',2.4),('GNG',1.4),('GNN',.6),('NGG',-.6),('NGN',-1.4),('NNG',-2.4),('NNN',-3.2)]}
    for level in range(1,4):
        previous=dict(level_nodes[level-1])
        for word,y in level_nodes[level]:
            parent_y=previous[word[:-1]]
            ax.plot([level-1,level],[parent_y,y],color=BLUE,lw=1)
            ax.text(level-.45,(parent_y+y)/2,('G: 1/3' if word[-1]=='G' else 'N: 2/3'),fontsize=9,ha='center',va='center',bbox={'facecolor':'white','edgecolor':'none','pad':1})
            if level==3:ax.text(3.1,y,word+('  ✓' if word.count('G')>=2 else ''),va='center',fontsize=10)
    ax.set_xlim(-.1,3.9);ax.set_ylim(-3.5,3.5);ax.axis('off')
    finish(fig,'BasicMath-F4-2022-tree.png')
    fig,ax=plt.subplots(figsize=(6,3.4))
    ax.add_patch(Circle((-1.15,0),.9,fill=False,color=BLUE,lw=1.7));ax.add_patch(Circle((1.15,0),.9,fill=False,color=BLUE,lw=1.7))
    ax.plot([-2.4,2.6,2.6,-2.4,-2.4],[-1.4,-1.4,1.5,1.5,-1.4],color=BLUE,lw=1)
    ax.text(-1.15,0,'15, 45',ha='center');ax.text(1.15,0,'30, 60',ha='center');ax.text(-1.15,1.1,'A',ha='center');ax.text(1.15,1.1,'B',ha='center');ax.text(2.1,-1.1,'75',ha='center');ax.text(2.5,1.7,'Universal set',ha='right',fontsize=10)
    ax.set_aspect('equal');ax.set_xlim(-2.6,2.8);ax.set_ylim(-1.6,1.9);ax.axis('off');finish(fig,'BasicMath-F4-2023-venn.png')
    fig,ax=plt.subplots(figsize=(7,3.6))
    for shirt,y0 in [('Blue',1.5),('Red',-1.5)]:
        ax.plot([0,1],[0,y0],color=BLUE);ax.text(.4,y0/2,'1/2',fontsize=10,bbox={'facecolor':'white','edgecolor':'none'})
        ax.text(1,y0,shirt,ha='center',bbox={'facecolor':'white','edgecolor':'none'})
        for trouser,delta in [('Black',.8),('Green',0),('Yellow',-.8)]:
            y1=y0+delta;ax.plot([1,2],[y0,y1],color=BLUE);ax.text(1.5,(y0+y1)/2,'1/3',fontsize=10,bbox={'facecolor':'white','edgecolor':'none'});ax.text(2.1,y1,f'{shirt} + {trouser}',fontsize=10,va='center')
    ax.set_xlim(-.1,3.3);ax.set_ylim(-2.6,2.6);ax.axis('off');finish(fig,'BasicMath-F4-2023-outfits.png')
    fig,ax=plt.subplots(figsize=(5,4.5))
    P=np.array([0.,0.]);Q=np.array([2*np.sqrt(3),2.]);R=Q+np.array([-1.5,1.5*np.sqrt(3)])
    ax.plot([P[0],Q[0],R[0]],[P[1],Q[1],R[1]],color=BLUE,lw=2);ax.plot([0,R[0]],[0,R[1]],'--',color='#267144')
    for label,p in [('P',P),('Q',Q),('R',R)]:ax.text(p[0]+.12,p[1]-.15,label)
    for p in [P,Q]:ax.annotate('',xy=(p[0],p[1]+1.4),xytext=p,arrowprops={'arrowstyle':'->','color':'#58656e'});ax.text(p[0]-.2,p[1]+1.4,'N',fontsize=10)
    ax.text(1.6,.65,'4 km\nN60°E',ha='center',fontsize=10);ax.text(3.2,3.6,'3 km\nN30°W',ha='left',fontsize=10)
    ax.set_aspect('equal');ax.set_xlim(-.6,4.8);ax.set_ylim(-.5,5.5);ax.axis('off');finish(fig,'BasicMath-F4-2023-bearings.png')
    fig,ax=plt.subplots(figsize=(6.8,3.8))
    edges=np.arange(39.5,100,10);freq=[2,4,7,9,5,3]
    ax.bar(edges[:-1],freq,width=10,align='edge',color='#edf4f8',edgecolor=BLUE)
    ax.plot([69.5,79.5],[9,5],color='#267144');ax.plot([69.5,79.5],[7,9],color='#267144');mode=69.5+10/3
    ax.axvline(mode,0,(23/3)/10,color='#267144',linestyle='--');ax.text(mode+1,3,'Mode\n72.83',color='#267144',fontsize=10)
    ax.set_xticks(edges);ax.set_xlabel('Marks (continuous class boundaries)');ax.set_ylabel('Frequency');ax.set_ylim(0,10);ax.set_yticks(range(11));fig.tight_layout();finish(fig,'BasicMath-F4-2023-histogram.png')
    fig,ax=plt.subplots(figsize=(5.3,5.3))
    points=np.array([[1,3],[2,5],[4,1],[1,3]])
    ax.plot(points[:,0],points[:,1],'-o',color=BLUE,label='ABC');ax.plot(-points[:,0],-points[:,1],'--o',color='#267144',label='A′B′C′')
    for label,p in zip('ABC',points[:3]):ax.text(p[0]+.15,p[1]+.15,label,color=BLUE);ax.text(-p[0]+.15,-p[1]-.4,label+'′',color='#267144')
    ax.axhline(0,color='#58656e',lw=1);ax.axvline(0,color='#58656e',lw=1);ax.set_xlim(-5,5);ax.set_ylim(-6,6);ax.set_xticks(range(-5,6));ax.set_yticks(range(-6,7));ax.grid(alpha=.2);ax.set_aspect('equal');ax.set_xlabel('x');ax.set_ylabel('y');ax.legend(loc='upper left');fig.tight_layout();finish(fig,'BasicMath-F4-2023-rotation.png')
    fig,ax=plt.subplots(figsize=(6.8,3.8))
    x=[64.5,69.5,74.5,79.5,84.5,89.5,94.5,99.5];y=[0,10,22,43,49,58,62,66]
    ax.plot(x,y,'o-',color=BLUE,lw=2);ax.set_xticks(x);ax.set_yticks(range(0,71,10));ax.set_ylim(0,70);ax.set_xlabel('Marks (upper class boundaries)');ax.set_ylabel('Cumulative frequency');ax.grid(alpha=.2);fig.tight_layout();finish(fig,'BasicMath-F4-2024-ogive.png')
    fig,ax=plt.subplots(figsize=(6,3.4))
    ax.add_patch(Circle((-.65,0),1.2,fill=False,color=BLUE,lw=1.7));ax.add_patch(Circle((.65,0),1.2,fill=False,color=BLUE,lw=1.7))
    ax.text(-1.1,0,'15',ha='center');ax.text(0,0,'3',ha='center');ax.text(1.1,0,'17',ha='center')
    ax.text(-1,1.45,'Goats',ha='center');ax.text(1,1.45,'Cows',ha='center');ax.text(2,-1.2,'Neither: 0',ha='center')
    ax.set_aspect('equal');ax.set_xlim(-2.1,2.8);ax.set_ylim(-1.6,1.8);ax.axis('off');finish(fig,'BasicMath-F4-2025-venn.png')
