import textwrap, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse, Rectangle, Polygon, Circle
INK="#111827"; BL="#dbeafe"; GR="#dcfce7"; AM="#fef3c7"; RD="#fee2e2"; GY="#f3f4f6"; PU="#ede9fe"
FS=7.6
def canvas(w,h):
    fig=plt.figure(figsize=(w,h),dpi=220); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,w); ax.set_ylim(0,h); ax.axis("off"); return fig,ax
def T(ax,x,y,s,fs=FS,bold=False,ha="center",color=INK,style="normal"):
    ax.text(x,y,s,fontsize=fs,ha=ha,va="center",fontweight="bold" if bold else "normal",color=color,fontstyle=style,linespacing=1.15)
def B(ax,x,y,w,h,s,fc="white",fs=FS,bold=False,dashed=False,r=0.06):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle=f"round,pad=0,rounding_size={r}",fc=fc,ec=INK,lw=0.8,ls="--" if dashed else "-"))
    T(ax,x,y,s,fs,bold)
def D(ax,x,y,w,h,s,fc=AM,fs=FS-0.4):
    ax.add_patch(Polygon([(x,y+h/2),(x+w/2,y),(x,y-h/2),(x-w/2,y)],fc=fc,ec=INK,lw=0.8)); T(ax,x,y,s,fs)
def O(ax,x,y,w,h,s,fc="white",fs=FS):
    ax.add_patch(Ellipse((x,y),w,h,fc=fc,ec=INK,lw=0.8)); T(ax,x,y,s,fs)
def A(ax,p,q,s=None,dashed=False,fs=FS-0.8,off=(0,0.09),both=False):
    ax.annotate("",xy=q,xytext=p,arrowprops=dict(arrowstyle="<|-|>" if both else "-|>",lw=0.8,color=INK,ls="--" if dashed else "-",shrinkA=0,shrinkB=0,mutation_scale=7))
    if s: T(ax,(p[0]+q[0])/2+off[0],(p[1]+q[1])/2+off[1],s,fs,style="italic")
def P(ax,pts,s=None,sp=None,dashed=False,fs=FS-0.8):
    for a,b in zip(pts[:-2],pts[1:-1]): ax.plot([a[0],b[0]],[a[1],b[1]],color=INK,lw=0.8,ls="--" if dashed else "-")
    A(ax,pts[-2],pts[-1],dashed=dashed)
    if s: T(ax,sp[0],sp[1],s,fs,style="italic")
def save(fig,name): fig.savefig(f"img/{name}.png",facecolor="white"); plt.close(fig)

# 1 architecture
fig,ax=canvas(6.8,4.9)
B(ax,0.62,4.55,0.9,0.4,"Student",GY,bold=True); B(ax,2.6,4.55,2.3,0.5,"React Frontend\n(Vite, Tailwind, Recharts)",BL)
A(ax,(1.07,4.55),(1.45,4.55)); A(ax,(2.6,4.3),(2.6,3.98),"HTTP / JSON",off=(0.55,0))
ax.add_patch(Rectangle((0.2,1.0),5.05,2.95,fc="#f9fafb",ec=INK,lw=0.8)); T(ax,2.72,3.8,"FastAPI Backend (Python 3.11, Pydantic, Uvicorn)",FS,True)
xs=[0.88,2.02,3.16,4.3]; r1=["Resume Upload\n& Text\nExtraction","NLP Skill\nExtraction","Student\nProfile\nCreation","Career\nRecommen-\ndation Engine"]
r2=["Interview,\nRoadmap &\nChatbot","LLM\nIntegration\n(llm_service)","Skill Gap\nAnalysis","Job Description\nComparison"]
for x,t in zip(xs,r1): B(ax,x,3.1,1.0,0.7,t,BL)
for x,t in zip(xs,r2): B(ax,x,1.85,1.0,0.7,t,GR if "LLM" in t or "Interview" in t else AM)
for a,b in zip(xs[:-1],xs[1:]): A(ax,(a+0.5,3.1),(b-0.5,3.1)); A(ax,(b-0.5,1.85),(a+0.5,1.85))
A(ax,(4.3,2.75),(4.3,2.2))
B(ax,6.05,3.1,1.25,0.6,"SQLite\n(profile, history)",GY); B(ax,6.05,1.85,1.25,0.6,"Ollama\nLlama 3.2:3b",PU)
A(ax,(3.16+0.5,3.1+0.0),(5.42,3.1),dashed=True,both=False) if False else None
A(ax,(4.8,3.1),(5.42,3.1),dashed=True,both=True); A(ax,(2.52,1.55),(2.52,1.55)) if False else None
P(ax,[(2.02,1.5),(2.02,1.2),(5.1,1.2),(5.1,1.85),(5.42,1.85)],None,dashed=True)
B(ax,2.7,0.5,3.0,0.45,"Results Dashboard (charts, tables, roadmap)",BL,bold=True)
A(ax,(2.7,1.0),(2.7,0.73)); P(ax,[(1.2,0.5),(0.08,0.5),(0.08,4.55),(0.17,4.55)],"results",(0.3,2.5))
fig.savefig("img/fig_architecture.png",facecolor="white"); plt.close(fig)

# 2 DFD L0
fig,ax=canvas(6.8,3.3)
B(ax,0.85,1.65,1.3,0.8,"Student",GY,bold=True); O(ax,3.4,1.65,1.9,1.5,"0\nCareerCompass AI\nSystem",BL,bold if False else FS+0.4)
B(ax,6.0,1.65,1.3,0.8,"Ollama\n(Llama 3.2:3b)",PU)
A(ax,(1.5,1.95),(2.45,1.95),"Resume, job description,\nrole, answers, questions",off=(0,0.4)); A(ax,(2.45,1.35),(1.5,1.35),"Skills, recommendations,\ngap report, roadmap, feedback",off=(0,-0.4))
A(ax,(4.35,1.95),(5.35,1.95),"Prompts",off=(0,0.17)); A(ax,(5.35,1.35),(4.35,1.35),"Generated text",off=(0,-0.17))
T(ax,3.4,0.25,"Level 0 data flow (context diagram)",FS,style="italic")
fig.savefig("img/fig_dfd0.png",facecolor="white"); plt.close(fig)

# 3 DFD L1
fig,ax=canvas(6.8,5.0)
B(ax,0.5,3.3,0.8,0.6,"Student",GY,bold=True); B(ax,6.35,2.4,0.8,0.7,"Ollama\nLLM",PU)
pos={"P1":(1.9,4.2,"1.0\nResume\nProcessing"),"P2":(3.45,4.2,"2.0\nSkill\nExtraction"),"P3":(5.0,4.2,"3.0\nCareer\nRecommend."),
     "P4":(1.9,2.4,"4.0\nJob Description\nAnalysis"),"P5":(3.45,2.4,"5.0\nSkill Gap\nAnalysis"),"P6":(5.0,2.4,"6.0\nGenAI Content\nGeneration")}
for k,(x,y,t) in pos.items(): O(ax,x,y,1.3,0.95,t,BL if k in("P1","P2","P3") else (AM if k in("P4","P5") else GR),FS-0.6)
A(ax,(0.9,3.5),(1.4,4.0),"resume",off=(-0.15,0.1)); A(ax,(2.55,4.2),(2.8,4.2)); A(ax,(4.1,4.2),(4.35,4.2),"skills",off=(0,0.12))
A(ax,(0.9,3.1),(1.4,2.55),"JD / role",off=(-0.15,-0.1)); A(ax,(2.55,2.4),(2.8,2.4)); A(ax,(3.45,3.72),(3.45,2.88),"skills",off=(0.3,0))
A(ax,(4.1,2.4),(4.35,2.4),"gaps"); A(ax,(5.65,2.4),(5.95,2.4),dashed=False,both=True)
B(ax,2.0,0.7,2.3,0.45,"D1  Skill Catalogue (JSON)",GY); B(ax,4.9,0.7,2.4,0.45,"D2  Profile & History (SQLite)",GY)
A(ax,(2.0,0.93),(2.0,1.92),dashed=True); A(ax,(3.0,0.93),(3.3,1.92),dashed=True); A(ax,(2.4,0.93),(3.2,3.72),dashed=True) if False else None
P(ax,[(1.45,0.93),(1.45,1.5),(0.5,1.5),(0.5,2.98)] ,None,dashed=True) if False else None
A(ax,(4.9,0.93),(4.9,1.92),dashed=True,both=True)
P(ax,[(5.0,4.68),(5.0,4.78),(0.5,4.78),(0.5,3.6)],"results shown on dashboard",(2.9,4.88))
T(ax,3.4,0.15,"Level 1 data flow (dashed = data store access)",FS-0.4,style="italic")
fig.savefig("img/fig_dfd1.png",facecolor="white"); plt.close(fig)

# 4 use case
fig,ax=canvas(6.8,5.3)
ax.add_patch(Rectangle((1.7,0.15),3.5,5.0,fc="#fafafa",ec=INK,lw=0.8)); T(ax,3.45,4.98,"CareerCompass AI",FS,True)
uc=["Upload Resume","View Extracted Skills","Get Career Recommendations","Select Career Role","Paste Job Description","Analyze Skill Gap","Generate Learning Roadmap","Practise Interview","Chat with Career Bot"]
ys=[4.55-i*0.47 for i in range(9)]
for y,t in zip(ys,uc): O(ax,3.45,y,2.9,0.38,t,BL if "Roadmap" not in t and "Interview" not in t and "Chat" not in t else GR,FS-0.3)
ax.plot([0.6,0.6],[2.55,2.15],color=INK,lw=1); ax.add_patch(Circle((0.6,2.8),0.13,fc="white",ec=INK,lw=1)); ax.plot([0.6,0.6],[2.67,2.2],color=INK,lw=1)
ax.plot([0.38,0.82],[2.5,2.5],color=INK,lw=1); ax.plot([0.6,0.4],[2.2,1.85],color=INK,lw=1); ax.plot([0.6,0.8],[2.2,1.85],color=INK,lw=1); T(ax,0.6,1.6,"Student",FS,True)
for y in ys: ax.plot([0.85,2.0],[2.4,y],color=INK,lw=0.5)
ax.plot([6.2,6.2],[2.55,2.15],color=INK,lw=1); ax.add_patch(Circle((6.2,2.8),0.13,fc="white",ec=INK,lw=1)); ax.plot([6.2,6.2],[2.67,2.2],color=INK,lw=1)
ax.plot([5.98,6.42],[2.5,2.5],color=INK,lw=1); ax.plot([6.2,6.0],[2.2,1.85],color=INK,lw=1); ax.plot([6.2,6.4],[2.2,1.85],color=INK,lw=1); T(ax,6.2,1.45,"Ollama LLM\n(secondary actor)",FS-0.6,True)
for y in ys[6:]: ax.plot([4.9,6.0],[y,2.4],color=INK,lw=0.5,ls="--")
fig.savefig("img/fig_usecase.png",facecolor="white"); plt.close(fig)


# 5 activity
fig,ax=canvas(6.8,6.9); dy=0.75
cx=2.6; ax.add_patch(Circle((cx,5.95+dy),0.1,fc=INK))
steps=[(5.5,"Upload resume (PDF / DOCX)","b"),(4.7,"File valid and readable?","d"),(3.9,"Extract text and resume sections","b"),(3.2,"Extract skills (NLP)","b"),(2.5,"Select role or paste job description","b"),(1.8,"Compute skill gap (Python)","b"),(1.1,"Request roadmap / interview from LLM","b")]
for y,t,k in steps:
    (B(ax,cx,y+dy,2.6,0.42,t,BL) if k=="b" else D(ax,cx,y+dy,2.6,0.7,t))
A(ax,(cx,5.85+dy),(cx,5.71+dy))
for (y1,t1,k1),(y2,t2,k2) in zip(steps[:-1],steps[1:]): A(ax,(cx,y1+dy-(0.35 if k1=="d" else 0.21)),(cx,y2+dy+(0.35 if k2=="d" else 0.21)))
T(ax,cx+0.2,4.15+dy,"Yes",FS-0.8,style="italic")
B(ax,5.6,4.7+dy,1.7,0.5,"Show error message",RD); A(ax,(3.9,4.7+dy),(4.75,4.7+dy),"No",off=(0,0.1)); P(ax,[(5.6,4.95+dy),(5.6,5.5+dy),(3.9,5.5+dy)])
D(ax,cx,0.4+dy,2.6,0.7,"Ollama available?"); A(ax,(cx,0.89+dy),(cx,0.75+dy))
B(ax,5.6,0.4+dy,1.8,0.55,"Show offline message;\nkeep Python results",RD); A(ax,(3.9,0.4+dy),(4.7,0.4+dy),"No",off=(0,0.1))
A(ax,(cx,0.05+dy),(cx,-0.1+dy)); T(ax,cx+0.25,0.66,"Yes",FS-0.8,style="italic")
B(ax,cx,0.52-0.0,2.8,0.42,"Validate LLM output and display dashboard",GR); A(ax,(cx,0.31),(cx,0.2)); ax.add_patch(Circle((cx,0.12),0.08,fc=INK))
P(ax,[(5.6,0.12+dy),(5.6,0.52),(4.0,0.52)])
fig.savefig("img/fig_activity.png",facecolor="white"); plt.close(fig)

# 6 sequence
fig,ax=canvas(6.8,5.0)
names=["Student","React UI","FastAPI","Skill Gap\nAnalyzer","LLM\nService","Ollama"]; xs=[0.6,1.7,2.85,3.95,5.05,6.15]
for x,n in zip(xs,names):
    B(ax,x,4.65,0.95,0.45,n,GY,bold=True); ax.plot([x,x],[4.4,0.15],color=INK,lw=0.6,ls="--")
msgs=[(0,1,"1 upload / select role"),(1,2,"2 POST /api/analyze"),(2,3,"3 compare skills"),(3,2,"4 gap result"),(2,4,"5 roadmap prompt"),(4,5,"6 /api/chat"),(5,4,"7 generated text"),(4,2,"8 validated roadmap"),(2,1,"9 JSON response"),(1,0,"10 show dashboard")]
y=4.1
for a,b,t in msgs:
    A(ax,(xs[a]+(0.06 if b>a else -0.06),y),(xs[b]+(-0.06 if b>a else 0.06),y),dashed=(b<a))
    T(ax,(xs[a]+xs[b])/2,y+0.12,t,FS-1.0,style="italic"); y-=0.4
fig.savefig("img/fig_sequence.png",facecolor="white"); plt.close(fig)

# 7 class
fig,ax=canvas(6.8,5.4)
def C(x,y,name,attrs,meths,fc=BL,w=1.5):
    h=0.3+0.17*(len(attrs)+len(meths))+0.1
    ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,fc="white",ec=INK,lw=0.8)); ax.add_patch(Rectangle((x-w/2,y+h/2-0.28),w,0.28,fc=fc,ec=INK,lw=0.8))
    T(ax,x,y+h/2-0.14,name,FS-0.2,True)
    yy=y+h/2-0.28-0.1
    for a in attrs: T(ax,x-w/2+0.05,yy,a,FS-1.3,ha="left"); yy-=0.17
    ax.plot([x-w/2,x+w/2],[yy+0.08,yy+0.08],color=INK,lw=0.5)
    for m in meths: T(ax,x-w/2+0.05,yy-0.02,m,FS-1.3,ha="left"); yy-=0.17
    return h
cols=[0.85,2.5,4.15,5.8]; r=[4.6,2.75,0.85]
C(cols[0],r[0],"ResumeParser",["-allowed_ext","-max_mb"],["+extract_text()","+parse_resume()","+mask_pii()"])
C(cols[1],r[0],"SkillExtractor",["-skill_catalog"],["+extract_skills()","+load_data()"])
C(cols[2],r[0],"JobDescription\nAnalyzer",["-patterns"],["+analyze_job_description()"],AM)
C(cols[3],r[0],"Database",["-db_path"],["+save_profile()","+save_history()"],GY)
C(cols[0],r[1],"CareerRecommender",["-roles"],["+recommend_careers()"],AM)
C(cols[1],r[1],"SkillGapAnalyzer",["-partial_credit"],["+analyze_gap()","+analyze_for_role()"],AM)
C(cols[2],r[1],"SemanticMatcher",["-backend"],["+best_match()"],AM)
C(cols[3],r[1],"LLMService",["-model","-timeout"],["+generate()","+validate_output()"],GR)
C(cols[1],r[2],"RoadmapGenerator",[],["+generate_roadmap()"],GR)
C(cols[2],r[2],"InterviewGenerator",[],["+questions()","+feedback()"],GR)
C(cols[3],r[2],"Chatbot",[],["+reply()"],GR)
A(ax,(1.6,4.6),(1.75,4.6)); A(ax,(3.4,4.6),(3.4+0.0,4.6)) if False else None
A(ax,(3.4,4.45),(2.6+0.15,4.45+0.0)) if False else None
A(ax,(3.4,4.5),(3.25,4.5)) if False else None
A(ax,(3.4,4.55),(3.25,4.55)); T(ax,3.32,4.72,"",FS)
A(ax,(1.6,2.75),(1.75,2.75)) if False else None
A(ax,(1.7,2.75),(1.75,2.75)) if False else None
A(ax,(1.6,2.75),(1.75,2.75))
A(ax,(3.25,2.75),(3.4,2.75)); T(ax,3.32,2.9,"",FS)
A(ax,(4.15,3.95),(3.25+0.8,3.55),None) if False else None
P(ax,[(4.15,4.23),(4.15,3.75),(2.5,3.75),(2.5,3.22)])
A(ax,(5.8,2.0),(5.8,2.35)) if False else None
A(ax,(5.8,3.3),(5.8,4.05),dashed=True)
for x,hh in ((2.5,.57),(4.15,.74),(5.8,.57)):
    top=0.85+hh/2
    P(ax,[(x,top),(x,1.9),(5.8,1.9),(5.8,2.12)] if x!=5.8 else [(x,top),(x,2.12)])
T(ax,3.4,0.12,"Logical class diagram; arrows show 'uses' relationships (the code implements these as module-level functions)",FS-1.3,style="italic")
fig.savefig("img/fig_class.png",facecolor="white"); plt.close(fig)

# 8 resume workflow
fig,ax=canvas(6.8,3.3)
t1=["Student uploads\nPDF / DOCX","Validate type,\nsize, content","Extract text\n(pypdf / python-docx)","Clean text and\nsplit sections"]
t2=["Structured profile\n(JSON)","Mask email and\nphone numbers","Match skills with\ncatalogue + aliases","Detect education,\nprojects, certificates"]
xs=[0.85,2.4,3.95,5.5]
for x,t in zip(xs,t1): B(ax,x,2.5,1.3,0.7,t,BL)
for a,b in zip(xs[:-1],xs[1:]): A(ax,(a+0.65,2.5),(b-0.65,2.5))
for x,t in zip(xs,t2): B(ax,x,1.0,1.3,0.7,t,GR if x==0.85 else AM)
for a,b in zip(xs[:-1],xs[1:]): A(ax,(b-0.65,1.0),(a+0.65,1.0))
# row2 flows right->left: detect -> skills -> mask -> profile
P(ax,[(5.5,2.15),(5.5,1.35)]) if False else A(ax,(5.5,2.15),(5.5,1.35))
B(ax,3.4,0.2,5.0,0.3,"Output: skills, sections, improvement tips, AI summary (LLM) shown on the Resume Dashboard",GY,FS-0.8) if False else None
T(ax,3.4,0.25,"Files are processed in memory only and are never stored on disk",FS-0.4,style="italic")
fig.savefig("img/fig_resume_flow.png",facecolor="white"); plt.close(fig)

# 9 skill gap workflow
fig,ax=canvas(6.8,3.9)
B(ax,0.55,3.2,0.9,0.62,"Resume skills\n+ required\nskills",BL,FS-0.6); B(ax,1.6,3.2,0.9,0.62,"Normalise\nskill names",BL,FS-0.6)
xs=[2.75,3.95,5.15]
D(ax,xs[0],3.2,1.1,0.8,"Exact\nmatch?"); D(ax,xs[1],3.2,1.1,0.8,"Related skill\npresent?"); D(ax,xs[2],3.2,1.1,0.8,"Similarity\n>= 0.80?")
A(ax,(1.0,3.2),(1.15,3.2)); A(ax,(2.05,3.2),(2.2,3.2))
A(ax,(3.3,3.2),(3.4,3.2),"No",off=(0,0.1)); A(ax,(4.5,3.2),(4.6,3.2),"No",off=(0,0.1))
B(ax,6.3,3.2,0.85,0.55,"MISSING",RD,bold=True); A(ax,(5.7,3.2),(5.875,3.2),"No",off=(0,0.1))
B(ax,xs[0],1.85,1.0,0.5,"MATCHED",GR,bold=True); B(ax,xs[1],1.85,1.0,0.5,"PARTIAL\n(related)",AM); B(ax,xs[2],1.85,1.0,0.5,"PARTIAL\n(semantic)",AM)
for x in xs: A(ax,(x,2.8),(x,2.1),"Yes",off=(0.2,0))
B(ax,3.4,0.55,3.7,0.5,"Match % = matched / required x 100\nWeighted coverage = (matched + 0.5 x partial) / required x 100",PU,FS-0.4)
for x in xs: A(ax,(x,1.6),(min(max(x,2.6),4.2),0.8))
P(ax,[(6.3,2.92),(6.3,0.55),(5.25,0.55)])
fig.savefig("img/fig_gap_flow.png",facecolor="white"); plt.close(fig)

# 10 GenAI workflow
fig,ax=canvas(6.8,4.4)
B(ax,0.85,3.5,1.3,0.7,"Deterministic\nresults (skills,\ngaps, scores)",BL); B(ax,2.5,3.5,1.3,0.7,"Prompt builder\n(role, rules,\nJSON format)",AM)
B(ax,4.15,3.5,1.3,0.7,"LLM Service\nHTTP request",GR); B(ax,5.8,3.5,1.3,0.7,"Ollama\nLlama 3.2:3b",PU)
for a,b in ((0.85,2.5),(2.5,4.15),(4.15,5.8)): A(ax,(a+0.65,3.5),(b-0.65,3.5))
B(ax,5.8,2.1,1.3,0.6,"Raw LLM\noutput",PU); A(ax,(5.8,3.15),(5.8,2.4))
D(ax,4.0,2.1,1.5,0.85,"Output valid?\n(format, length,\nno fake URLs)"); A(ax,(5.15,2.1),(4.75,2.1))
B(ax,2.1,2.1,1.5,0.6,"Display on\ndashboard",BL); A(ax,(3.25,2.1),(2.85,2.1),"Yes",off=(0,0.1))
B(ax,4.0,0.8,1.8,0.6,"Fallback template\n+ warning message",RD); A(ax,(4.0,1.67),(4.0,1.1),"No",off=(0.2,0))
P(ax,[(3.1,0.8),(2.1,0.8),(2.1,1.8)])
B(ax,0.85,1.1,1.45,0.9,"If Ollama is\nunreachable: show a\nclear error; Python\nresults remain",RD,FS-0.8,dashed=True); 
T(ax,3.4,0.2,"LLM writes explanations only; scores come from Python rules",FS-0.4,style="italic")
fig.savefig("img/fig_genai_flow.png",facecolor="white"); plt.close(fig)
