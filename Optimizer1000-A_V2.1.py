#================================================================================================
#Import von benötigten Bibliotheken
#================================================================================================

#GUI
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
#Bibliotekten für Interaktionen mit dem (Betriebs)system
import os
import shutil
#Automatatisierung über GUI (Bewegung Maus, Eingabe von Text, etc.)
import pyautogui
import pydirectinput
#Zeit
import time
#Handling von Daten (Kovertieren und Co.)
import numpy as np
from numpy import mean, sqrt, square

#==================================================================================================
#Definition von später genutzen Funktionen ab hier:
#==================================================================================================
#CWD = current working directory --> Arbeitsverzeichnis in dem das Programm Dateien ablegt und abruft
#Prüfen ob CWD festgelegt wurde
def check_CWD():
    if PageOne.CWD=="":
        tk.messagebox.showwarning(title="Achtung!",message="Bitte Arbeitsverzeichnis festlegen!")
        set_CWD()
    
#Legt CWD fest
def set_CWD():
    #Dialogfenster
    PageOne.CWD = filedialog.askdirectory(parent=root,title='Arbeitsverzeichnis wählen!')
    cwd_conv=PageOne.CWD
    #Ersetzt im String die / durch \\
    PageOne.CWD_win=cwd_conv.replace('/', "\\")
    cwd_info="Das Arbeitsverzeichnis für die Simulation ist:\n %s"%(PageOne.CWD)
    #Kopieren der benötigten Dateien ins Arbeitsverzeichnis
    shutil.copy(MyApp.prog_path+"\\maxvmis.mac", PageOne.CWD)
    shutil.copy(MyApp.prog_path+"\\SKO_Optimizer.txt", PageOne.CWD)

    #Hinweis, dass Arbeitsverzeichnis erfolgreich festgelegt wurde
    if PageOne.CWD != "":
        tk.messagebox.showinfo(title="Arbeitsverzeichnis",message=cwd_info)

#Tool für die Konfiguration
def xy_config():
    #Fenster mit Hinweisen zum Starten der Konfiguration
    ask=tk.messagebox.askokcancel("Konfiguration Starten", "Klicken Sie auf \"Ok\" um die Konfiguration zu starten.\n\nBewegen Sie anschließend die Maus über die \nANSYS Command Promt.\n\nDie Position wird nach 10 Sekunden angezeigt.", )
    if ask == True:
        time.sleep(10)
        (x,y)=pyautogui.position()
        xy_pos="Bitten tragen Sie die folgenden Werte in die config-Datei ein:\nX-Postition: %s\nY-Position: %s" %(x,y)
        tk.messagebox.showinfo(title="Konfiguration abgeschlossen", message=xy_pos)

#Konvertierung der Knotenspannungen aus ADAMS
#Nach Komponenten XYZ:
def RMS_conv_XYZ(datei,path):

    #Festlegung Speicherort und Name der Datei   
    path=path+r"\rms_tensor.txt"

    #Faktor EH für spätere Erweiterung (Anpassung Einheiten oder Ähnliches)  
    EH=1
    #Daten aus importierter Datei einlesen:
    with open(datei) as d:
        data=np.genfromtxt((line.replace(",",".")for line in d), skip_header=7, delimiter="\t")

    size=np.shape(data)
    rows=size[0]
    coll=int(size[1]/6)

    #rms-Werte der Knotenspannungen berechnen
    rmsx=np.zeros(coll)
    rmsy=np.zeros(coll)
    rmsz=np.zeros(coll)
    rmsxy=np.zeros(coll)
    rmsyz=np.zeros(coll)
    rmszx=np.zeros(coll)
    rms=0
    for i in range(coll):
  
        rms=sqrt(mean(square(data[:,i])))
        rmsx[i]=rms*EH

    for i in range(coll):
        rms=sqrt(mean(square(data[:,i+coll])))
        rmsy[i]=rms*EH

    for i in range(coll):
        rms=sqrt(mean(square(data[:,i+2*coll])))
        rmsz[i]=rms*EH

    for i in range(coll):
        rms=sqrt(mean(square(data[:,i+3*coll])))
        rmsxy[i]=rms*EH

    for i in range(coll):
        rms=sqrt(mean(square(data[:,i+4*coll])))
        rmsyz[i]=rms*EH

    for i in range(coll):
        rms=sqrt(mean(square(data[:,i+5*coll])))
        rmszx[i]=rms*EH

    #Datei mit konvertierten Spannungswerten erstellen
    out=open(path,"w")
    out.write("/nopr\ninistate,set,csys,0 \ninistate,set,dtyp,s \ninistate,set,node,1 \n")

    for n in range(5,coll+5):
        out.write("inistate,define,%d,,,,%f,%f, %f, %f, %f, %f \n" %(n-4,rmsx[n-5],rmsy[n-5],rmsz[n-5],rmsxy[n-5],rmsyz[n-5],rmszx[n-5] ))

    out.close()

#Von Mieses:
def RMS_conv(datei,path):

    #Festlegung Speicherort und Name der Datei   
    path=path+r"\rms_tensor.txt"
    
    #Faktor EH für spätere Erweiterung (Anpassung Einheiten etc.)  
    EH=1
    #Daten aus importierter Datei einlesen:
    with open(datei) as d:
        data=np.genfromtxt((line.replace(",",".")for line in d), skip_header=7, delimiter="\t")

    size=np.shape(data)
    rows=size[0]
    coll=size[1]
    #print(coll)
    #rms berechnen
    rmsv=np.zeros(coll)
    rms=0
    for i in range(coll):
      rms=sqrt(mean(square(data[:,i])))
      rmsv[i]=rms

    out=open(path,"w")
    out.write("/nopr \ninistate,set,csys,0 \ninistate,set,dtyp,s \ninistate,set,node,1 \n")

    for n in range(5,coll+5):
       out.write("inistate,define,%d,,,,%f,%f, %f, %f, %f, %f \n" %(n-4,rmsv[n-5],rmsv[n-5],rmsv[n-5],rmsv[n-5],rmsv[n-5],rmsv[n-5] ))
  
    out.close()

#Funktionen um die Programme über den Optimierer zu öffnen
#Später ist für den jeweiligen Rechner das Öffnen von Ansys zu implementieren
def open_ansys():
   os.startfile(MyApp.ansys_path)
   return
#ASAMS öffnen --> ebenfalls spätere Konfiguration erforderlich
def open_adams():
    os.startfile(MyApp.adams_path)
    return
#Dialogfenster zum Importieren und Speichern der Knotenspannungen aus ADAMS
def open_file(opt):
 file = filedialog.askopenfilename(parent=root,title='Datei öffnen') 
 if file != None:
        path=filedialog.askdirectory(title='Speicherort auswählen')
        if opt=="XYZ":
            RMS_conv_XYZ(file,path)
        else:
            RMS_conv(file,path)
 return

#Import des Adams Modells:
def import_adams(node_num,CWD,step_num):
    #Programm prüft welcher Schritt gerade ausgeführt wird, um entsprechende Anpassungen am Marko vorzunehmen
    #Schritt 0 entspricht dem ersten Import des Adams-Modells. Hier wird ein Dialogfenster geöffnet und die Datei kann eingelesen werden.
    if step_num==0:
        check_CWD
        adams_init_model=filedialog.askopenfilename(parent=root,title='Adams CMD-Datei auswählen')
        Import_Modelle.adams_init_model=adams_init_model
        Import_Modelle.adams_file_name=simpledialog.askstring("Input", "Bitte den Namen des Modells (Database) in Adams eingeben ",parent=root)
        Import_Modelle.adams_mod_name=simpledialog.askstring("Input", "Bitte den Namen des Bauteils in Adams ohne _flex eingeben ",parent=root)
        
        


    #Prüfung ob Datei erfolgreich eingelesen:
    if Import_Modelle.adams_init_model != None:
        adams_mod=Import_Modelle.adams_init_model
        #Parameter sim_para.list_stress_mode wird für einfacheres Handling umbenannt
        l=sim_para.list_stress_mode
        #Datei wird erstellt
        path=CWD+"/adams_mod.cmd"
        anz=str(node_num)
        if len(anz)>0:
            zahl=int(anz)
            L=""
            for i in range(1,zahl+1):
                if i<zahl:
                    L=L+str(i)+", "
                else:
                    L=L+str(i)

        with open(adams_mod) as in_mod:
            inp=in_mod.read()
        #Makro wird angepasst für den jeweiligen Schritt und gewünschten Spannungstyp erzeugt
        out=open(path,"w")
        out.write(inp)
        out.write("""
        if cond=("" == "interactive")
        int cont undisp cont=c_scripted
        int cont disp cont=c_interactive
        else
        int cont disp cont=c_scripted
        int cont undisp cont=c_interactive
        end
        if condition=((Eval(.gui.sim_int_panel.filesName)[1] != ""))
        if condition=()
            variable set variable_name = .gui.int_tsf_final_list string_value="" 
            file temporary_settings apply &
            file =  
        end
        end
        var set var = .mdi.errno int=0
        if cond=("Interactive" == "interactive")
        if cond=0
            simulation single reset
        end
        if cond=("End Time" == "Forever")
            simulation single trans &
                type             = auto_select   &
                initial_static   = no    &
                forever          = true               &
                
        else
            simulation single trans &
                type             = auto_select   &
                initial_static   = no    &
                        &
                end_time        = %s         &
                        &
                number_of_steps = %s

            end
        else
        simulation single scripted &
            sim_script_name =  &
            reset_before_and_after = 
        end
        IF condition=((Eval(.gui.sim_int_panel.filesName)[1] != ""))
        if condition=()
            variable set variable_name = .gui.sim_int_panel.run.file_to_tmp int = (eval(SET_TSF_FILE_ANALYSIS((eval(DB_DEFAULT(.system_defaults,"model"))),STOO(".gui.int_tsf_final_list"))))
            variable set variable_name = .gui.int_tsf_final_list string_value="" 
            file temporary_settings revert
        End
        End
        mdi gui_utl_check_sim alert_done=no alert_stop=no
        var set var = .mdi.errno int=0   ! in case a simulation is running
        interface field set field=message strings="" action=replace
        interface dialog_box undisplay dialog_box_name = .gui.msg_box
        interface dialog undisplay dialog=.gui.sim_int_panel
        """ %(sim_para.adams_time, sim_para.adams_step))#,sim_para.adams_time, sim_para.adams_step))
        out.write("var set var=.durability.comp_nodals.nod_list integer=%s \n" %(L))
        out.write("""  mdi durability nodal_plot  &
        analysis = .%s.Last_Run  &
        flex_body = .%s.%s_flex  &
        node_ids = .durability.comp_nodals.nod_list  &
        tensor_type = 1  &
        sigvm = %s  &
        sigx = %s  &
        sigy = %s   &
        sigz = %s  &
        tauxy = %s  &
        tauyz = %s  &
        tauzx = %s  &
        maxprin = 0  &
        minprin = 0  &
        maxshear= 0 &
        \n""" %(Import_Modelle.adams_file_name, Import_Modelle.adams_file_name, Import_Modelle.adams_mod_name,l[0],l[1],l[2],l[3],l[4],l[5],l[6]))

        out.write("""
        int dia dis dia=.gui.file_export
        int option exe option=.gui.file_export.type_opt
        file log comm=off
        interface dialog execute dialog=.gui.file_export undisplay=yes
        if cond=("spreadsheet" == "analysis" || "spreadsheet" == "request" || "spreadsheet" == "results" || "spreadsheet" == "graphics")
           int cont exe cont=.gui.file_export.analysis undisp=no
        elseif cond= (DB_EXISTS(".gui.file_export.spreadsheet"))
          int cont exe cont=.gui.file_export.spreadsheet  undisp=no
        file spread_sheet write  &
        file_name = "%s/node_stress_step_%s.tab"  &
        result_set_name = %s_flex_STRESS
        else
        int cont exe cont=.gui.file_export.cadexport undisp=no
        end
        interface dialog undisplay dialog=.gui.file_export
        var set var=.gui.file_export.unload int=(eval(UNLOAD_INTEROP()))
        """ %(CWD, str(step_num),Import_Modelle.adams_mod_name))
        out.close()
        
#Import des initialen ANSYS-Modells:
def import_ansys(CWD):
    #Prüfung ob CWD festgelegt wurde
    check_CWD()
    #Import des Modells über Dateidialog
    Import_Modelle.ansys_init_model=filedialog.askopenfilename(parent=root,title='ANSYS-Modell auswählen')
    if Import_Modelle.ansys_init_model != None:
        #Anzahl Knoten eingeben:
        Import_Modelle.node_num=simpledialog.askinteger("Input", "Bitte Knotenanzahl des importierten Modells eingeben",parent=root)
        #Knotennummern der attachment nodes (Knoten an denen die Randbedingungen angreifen) eingeben:
        attach_no_num=tk.simpledialog.askstring("Eingabe Knoten","Bitte \"attachment node\" Nummern eingeben", parent=root)
        attach_no_num=attach_no_num.split(",")
        attach_no_string="!=======MNF-File Erstellen\n\n/solu\n\nFLST, 5, %s, 1, ORDE, %s\n" %(len(attach_no_num), len(attach_no_num))
        for i in range(len(attach_no_num)):
            attach_no_string=attach_no_string+"FITEM,5,%s\n" %(attach_no_num[i])
        attach_no_string=attach_no_string+("Nsel,R,,,P51X \n/UNIT,SI \nLUMPM,ON \nsave \nADAMS,8,3,0")

        #ANSYS APDL-Skript für MNF-Erstellung generieren:
        path_mnf=CWD+"/ansys_mnf_mod.txt"
        with open(Import_Modelle.ansys_init_model) as in_mod:
            IN=in_mod.read()

        out=open(path_mnf,"w")
        out.write(IN)
        out.write("j=0\n")
        out.write("""!**** Optimierungsbereiche definieren
        allsel
        cm,optima1,elem
        cmgrp,Bereich,optima1
        allsel
        """)
        out.write(attach_no_string)
        out.close()
        Import_Modelle.ansys_mnf_mod=path_mnf
        ANSYS_sim_start(Import_Modelle.ansys_mnf_mod,PageOne.CWD)
        t=0
        while os.path.isfile(PageOne.CWD+"\\workflow.mnf") == False:
                time.sleep(1)
                t=t+1
                if t==sim_para.max_sim_time_ansys: #maximale Simulationszeit
                    tk.messagebox.showwarning(title=None,message="Simulation auf Grund von Zeitüberschreitung abgebrochen. \n Bitte Modelle überprüfen oder Simulationszeit erhöhen!")
                    break
        tk.messagebox.showinfo(title=None,message="Einlesen des ANSYS-Modells und Generation der MNF-Datei erfolgreich!")

        #ANSYS APDL-Skripft für SKO-Optimierung
        path_SKO=CWD+"/ansys_SKO_mod.txt"
        out=open(path_SKO,"w")
        out.write("""
        /solu
        /inp,rms_tensor,txt
        solve
        /post1
        set,1
        cmsel,s,Bereich
        maxvmis
        /post1
        set,1
        pletab,svmax
        /post1
        cmsel,s,Bereich
        E1 = ET
        etable,emodu,volu
        /solu
        /inp,SKO_Optimizer,txt
        /post1
        fini
        %s""" %(attach_no_string))
        out.close()
        Import_Modelle.ansys_SKO_mod=path_SKO
        
def adams_sim_start(stepnumber):
    #Programm ruft die Import funktion auf um das Makro für den jeweiligen Schritt zu erstellen
    import_adams(Import_Modelle.node_num, PageOne.CWD,stepnumber)
    #Simulation wird gestartet
    os.system("%s aview ru-st b %s" %(MyApp.adams_vers, PageOne.CWD_win+"\\adams_mod.cmd"))
    sol_path=PageOne.CWD+'\\node_stress_step_%s.tab' %(stepnumber)
    #Prüfschleife ob Simulation abgeschlossen ist und Ergebnisdatei erzeugt wurde
    t=0
    while os.path.isfile(sol_path) == False:
                time.sleep(1)
                t=t+1
                if t==sim_para.max_sim_time_adams:
                    tk.messagebox.showwarning(title=None,message="Simulation auf Grund von Zeitüberschreitung abgebrochen. \n Bitte Modelle überprüfen oder Simulationszeit erhöhen!")
                    break
    #Konvertierung für Import nach ANSYS
    if sim_para.stress_mode=="VM":
        RMS_conv(sol_path, PageOne.CWD)
    else:
        RMS_conv_XYZ(sol_path, PageOne.CWD)
    #Umbenennen der mnf-Datei
    os.rename(PageOne.CWD+"/workflow.mnf", PageOne.CWD+"/workflow-mnf_step_%d.mnf" %(stepnumber))
    
# ANSYS Automatisierung über GUI
def ANSYS_sim_start(modell,CWD):
    #Festlegung CWD für Ansys
    ansys_cwd="/CWD, '%s'" %(CWD)
    ls=list(modell)
    ansys_filename_strip="".join(ls[:len(modell)-4])
    ansys_mod="/inp, '%s',txt" %(ansys_filename_strip)
    x_pos=int(MyApp.x_pos)
    y_pos=int(MyApp.y_pos)
    time.sleep(1)
    pydirectinput.click(x=x_pos, y=y_pos)
    pydirectinput.click(x=x_pos, y=y_pos)
    pydirectinput.press('enter')
    pydirectinput.click(x=x_pos, y=y_pos) 
    pydirectinput.press('enter')
    pydirectinput.click(x=x_pos, y=y_pos)
    pyautogui.write(ansys_cwd)
    pydirectinput.press('enter')
    pyautogui.write(ansys_mod)
    pydirectinput.press('enter')
    

#Funktion zum Starten der Optimierungsschleife
def optimize(stepnumber,opt_step,max_step, sim_dir):
    #Prüfung ob alle Parameter definiert wurden
    if stepnumber=="" or max_step=="" or sim_dir=="" or sim_para.max_sim_time_adams=="" or sim_para.max_sim_time_ansys=="":
       tk.messagebox.showwarning(title=None,message="Mindestens eine der Variablen ist nicht definiert. \nBitte Simulationsparameter überprüfen!") 

    int(stepnumber)
    int(max_step)
    #Die erste Schleife beginnt mit der Adams-Simulation
    if stepnumber==1:
        adams_sim_start(stepnumber)
        stepnumber+=1
        #Funktion ruft sich selber erneut auf mit neuer Schrittnummer
        optimize(stepnumber,opt_step,max_step, sim_dir)

    elif stepnumber<=max_step:
        #Mögliche Erweitung mit wiederholter SKO-Optimierung
        #for i in range(opt_step):

        time.sleep(5)
        #Starten der Simulation mit ANSYS über GUI
        ANSYS_sim_start(Import_Modelle.ansys_SKO_mod, PageOne.CWD)
        #Programm wartet bis MNF-Datei erstellt wurde
        t=0 #Zeit für Simulation wird auf 0 gesetzt
        #Prüfen ob MNF Datei im CWD ist
        while os.path.isfile(PageOne.CWD+"\\workflow.mnf") == False:
            time.sleep(1)
            t=t+1
            if t==int(sim_para.max_sim_time_ansys): #maximale Simulationszeit
                tk.messagebox.showwarning(title=None,message="Simulation auf Grund von Zeitüberschreitung abgebrochen. \n Bitte Modelle überprüfen oder Simulationszeit erhöhen!")
                break
        #Wenn MNF erfolgreich erstellt wurde wird im nächsten Schritt Adams aufgerufen
        #Anteil Adams --> MNF wird eingelesen und Simulation durchgeführt, nach Abschluss werden die Knotenspannungen exportiert und konvertiert
        #das erfolgt alles durch das adams Macro, welches mit folgendem Befehl aufgerufen wird
        adams_sim_start(stepnumber)
        stepnumber+=1
        #Programm ruft sich selber mit erhöhter Schrittnummer auf
        optimize(stepnumber,opt_step,max_step, sim_dir)
    else:
        #Abschluss der Optimierung wird durch Fenster gemeldet
        tk.messagebox.showinfo(title=None,message="Optimierung abgeschlossen!")

#Funktion zum Testen verschiedener Sachen, kann nach belieben erweitert und angepasst werden
def DEBUG(file):
    print("")

#============================================================================================================================================

#Verschiedene Parameter zur Darstellung des GUI-Fensters
frame_styles = {"relief": "groove",
                "bd": 3, "bg": "#BEB2A7",
                "fg": "#073bb3", "font": ("Arial", 9, "bold")}

#=======================================================================================================================================
#Ab hier Definition der einzelnen Klassen bzw. Elementen der GUI
#=======================================================================================================================================

#Konfiguration der Anwendung:
class MyApp(tk.Tk):

    #Atribute:
    prog_path="" #Pfad in dem das Programm liegt
    #Daten aus dem Config-File
    ansys_path=""
    adams_path=""
    adams_vers=""
    x_pos=""
    y_pos=""
    
    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self, bg="#84CEEB", height=600, width=1024)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.frames = {}
        # aufrufbare "Seiten" in der GUI
        pages = ( PageOne, Some_Widgets, Optimierung, Import_Modelle,sim_para)
        for F in pages:
            frame = F(main_frame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        #Seite die beim Start des Programmes gezeigt wird:
        self.show_frame(PageOne)
        menubar = MenuBar(self)
        tk.Tk.config(self, menu=menubar)
        #Ermitteln des Programmverzeichnisses
        MyApp.prog_path=os.path.dirname(os.path.realpath(__file__))
        #Einlesen der Daten aus Config-File
        config_file=open(MyApp.prog_path+"\\config.txt", "r")
        lines=config_file.readlines()
        #.strip() entfernt \n am ende des Strings 
        MyApp.ansys_path=lines[1].strip()
        MyApp.adams_path=lines[3].strip()
        MyApp.adams_vers=lines[5].strip()
        MyApp.x_pos=lines[7].strip()
        MyApp.y_pos=lines[9].strip()
        #Definieren von Standardparametern
        #von Mieses Spannung als default definieren
        sim_para.Var3.set(2)
    
    #Allgemeine Funktionen des Programms
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def OpenNewWindow(self):
        OpenNewWindow()

    def Quit_application(self):
        self.destroy()
        
#Menüleiste:
class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        #Datei:
        menu_file = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Datei", menu=menu_file)
        menu_file.add_command(label="Start", command=lambda: parent.show_frame(PageOne))
        menu_file.add_separator()
        menu_file.add_command(label="Konfiguration", command=lambda: xy_config())
        menu_file.add_separator()
        menu_file.add_command(label="Beenden", command=lambda: parent.Quit_application())    
        #Modellerstellung:
        menu_pricing = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Modellerstellung", menu=menu_pricing)
        menu_pricing.add_command(label="ANSYS starten",command=lambda: open_ansys())
        menu_pricing.add_separator()
        menu_pricing.add_command(label="ADAMS starten",command=lambda: open_adams())
        menu_pricing.add_separator()
        menu_pricing.add_command(label="Modelle importieren", command=lambda: parent.show_frame(Import_Modelle))
        menu_pricing.add_separator()
        menu_pricing.add_command(label="Tools",command=lambda: parent.show_frame(Some_Widgets))
        #Optimierung:
        menu_operations = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Optimierung",menu=menu_operations)
        menu_operations.add_command(label="Optimierungsparameter", command=lambda: parent.show_frame(sim_para))
        menu_operations.add_separator()
        menu_operations.add_command(label="Optimierung starten", command=lambda: parent.show_frame(Optimierung))
        menu_positions = tk.Menu(menu_operations, tearoff=0)
        #Hilfe:
        menu_help = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Hilfe", menu=menu_help)
        menu_help.add_command(label="Hilfe anzeigen", command=lambda: parent.OpenNewWindow())

#Konfiguration der GUI Komponenten. Die weiteren Elemente erben Informationen aus dieser Klasse
class GUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.main_frame = tk.Frame(self, bg="#BEB2A7", height=600, width=1024)
        self.main_frame.pack(fill="both", expand="true")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

#Tools:
class Some_Widgets(GUI):  
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        #Definition der Funktion die, die Nummern für den Spannungsexport von ADAMS erzeugt
        def print_num(anz):
        
             if len(anz)>0:
                zahl=int(anz)
                L=""
                for i in range(1,zahl+1):
                    if i<zahl:
                        L=L+str(i)+","
                    else:
                        L=L+str(i)
               #Schreiben der Zahlen ins Textfeld
                T.delete("1.0",END)
                T.insert(END, L)                  
                return 
        
        #Rahmen für Anzeige der Nummern
        frame1 = tk.LabelFrame(self, frame_styles, text="Knotennummern für Export aus ADAMS")
        frame1.place(rely=0.05, relx=0.55, height=400, width=300)
        #Rahmen für Anzeige der Tools und Widgets
        frame2 = tk.LabelFrame(self, frame_styles, text="Tools")
        frame2.place(rely=0.05, relx=0.02, height=500, width=500)
        #Knopf zum Nummern generieren
        button1 = tk.Button(frame2, text="Nummern generieren", command=lambda: print_num(entry.get()))
        button1.place(x=300)
        #Knopf zum Konvertieren der Knotenspannungen (von Mises)
        button2 = tk.Button(frame2, text="Knotenspannungen (von Mieses) aus ADAMS kovertieren", command=lambda: open_file("vonMieses"))
        button2.pack(pady=50)
        #Knopf zum Konvertieren der Knotenspannungen (Spannungstensor)
        button3 = tk.Button(frame2, text="Knotenspannungen (Spannungstensor) aus ADAMS kovertieren", command=lambda: open_file("XYZ"))
        button3.pack() #pady=0
        #Texteingabefeld
        entry = tk.Entry(frame2, font=40)
        entry.place(relwidth=0.6, relheight=0.05)
        
        #Textfeld mit Scrollbar
        S=Scrollbar(frame1)
        T=Text(frame1, height=400, width=400)
        S.pack(side=RIGHT,fill="y")
        T.pack(side=LEFT, fill="y")
        S.config(command=T.yview)
        T.config(yscrollcommand=S.set)
        BNe= "<------ Bitte Anzahl der Knoten \neingeben"
        T.insert(END,BNe)
        
#Startseite:
class PageOne(GUI):

    CWD=""
    CWD_win=""

    def __init__(self, parent, controller):
        GUI.__init__(self, parent)
        label1 = tk.Label(self.main_frame, font=("Verdana", 20), text="Willkommen!")
        label1.pack(side="top")
        label2 = tk.Label(self.main_frame, font=("Verdana", 10), text="\n \n Zum Starten der Optimierung legen Sie zunächst das Arbeitsverzeichnis fest. \n Wählen Sie anschließend in den Reitern oben den gewünschten Einstiegspunkt.")
        label2.pack()
        button1 = tk.Button(self.main_frame, text="Arbeitsverzeichnis wählen", command=lambda: set_CWD())
        button1.pack()
       
#Simulationsparameter
class sim_para(GUI):
    
    #Attribute und Zuweisung der Default-Parameter
    max_step=int
    stepnumber=1
    Var3=None
    stress_mode="VM"
    list_stress_mode=["1","0","0","0","0","0","0","VON_MISES"]
    max_sim_time_ansys=120
    max_sim_time_adams=180
    adams_time="5.0"
    adams_step="200"


    def __init__(self, parent, controller):
        GUI.__init__(self,parent)
        
        #Funktionen zur Zuweisung der Variablen
        def def_max_step(max_step):
            sim_para.max_step=int(max_step)
        def def_stepnumber(stepnumber):
            sim_para.stepnumber=int(stepnumber)
        def def_sim_time_ansys(max_sim_time_ansys):
            sim_para.max_sim_time_ansys=int(max_sim_time_ansys)
        def def_sim_time_adams(max_sim_time_adams):
            sim_para.max_sim_time_adams=int(max_sim_time_adams)
        def def_adams_time(adams_time):
            sim_para.adams_time=(adams_time)
        def def_adams_step(adams_step):
            sim_para.adams_step=adams_step
        
        #Rahmen
        frame2 = tk.LabelFrame(self, frame_styles, text="Parameter für die Optimierung")
        frame2.place(rely=0.05, relx=0.1, height=500, width=600)
        #Eingabefelder Parameter für Simulation / Optimierung:
        #Anzahl maximaler Simulationsschritte / Durchläufe Optimierungsschleife
        entry = tk.Entry(frame2, font=40)
        entry.place(relwidth=0.5, relheight=0.05)
        button1 = tk.Button(frame2, text="Anzahl Simulationsschritte", command=lambda: def_max_step(entry.get()))
        button1.place(x=300)
        #Definition bei welchem Schritt der Programm in die Optimierung einsteigt
        #Als Standard ist 1 festgelegt (neue Simulation)
        entry2 = tk.Entry(frame2, font=40)
        entry2.place(relwidth=0.5, relheight=0.05, y=30)
        entry2.insert(0, sim_para.stepnumber)
        button2 = tk.Button(frame2, text="Startschritt", command=lambda: def_stepnumber(entry2.get()))
        button2.place(x=300, y=30)
        #Maximale Simulationszeit bis Abbruch für ANSYS
        entry3 = tk.Entry(frame2, font=40)
        entry3.place(relwidth=0.5, relheight=0.05, y=62.5)
        entry3.insert(0, sim_para.max_sim_time_ansys)
        button3 = tk.Button(frame2, text="maximale Simulationszeit ANSYS", command=lambda: def_sim_time_ansys(entry3.get()))
        button3.place(x=300, y=62.5)
        #Maximale Simulationszeit bis Abbruch für Adams
        entry4 = tk.Entry(frame2, font=40)
        entry4.place(relwidth=0.5, relheight=0.05, y=95)
        entry4.insert(0, sim_para.max_sim_time_adams)
        button4 = tk.Button(frame2, text="maximale Simulationszeit Adams", command=lambda: def_sim_time_adams(entry4.get()))
        button4.place(x=300, y=95)
        #Parameter für die Simulation in Adams
        label1=tk.Label(frame2, font=("Verdana", 8), text="Parameter für die Simulation IN Adams:", anchor="e", justify=LEFT )
        label1.place(x=5, y=140)
        #Maximale Simulationszeit in Adams
        entry5 = tk.Entry(frame2, font=40)
        entry5.place(relwidth=0.5, relheight=0.05, y=160)
        entry5.insert(0, sim_para.adams_time)
        button5 = tk.Button(frame2, text="Simulationszeit in Adams  (Format XX.X)", command=lambda: def_adams_time(entry5.get()))
        button5.place(x=300, y=160)
        #Schrittanzahl Admas
        entry6 = tk.Entry(frame2, font=40)
        entry6.place(relwidth=0.5, relheight=0.05, y=190)
        entry6.insert(0, sim_para.adams_step)
        button6 = tk.Button(frame2, text="Schritte in Adams", command=lambda: def_adams_step(entry6.get()))
        button6.place(x=300, y=190)

        #Auswahl von Mieses oder Tensor
        label2=tk.Label(frame2, font=("Verdana", 8), text="Bitte wählen Sie in welchem Format die Knotenspannung aus Adams exportiert \nund konvertiert werden soll:", anchor="e", justify=LEFT )
        label2.place(x=5, y=225)
        def sel():
            if sim_para.Var3.get() ==1:
                sim_para.stress_mode="XYZ"
                sim_para.list_stress_mode=["0","1","1","1","1","1","1","NORMAL_X"]
            else:
                sim_para.stress_mode="VM"
                sim_para.list_stress_mode=["1","0","0","0","0","0","0","VON_MISES"]
        
        sim_para.Var3 = IntVar()
        R1 = tk.Radiobutton(frame2, text="Spannungstensor", variable=sim_para.Var3, value=1, command=sel)
        R1.place(x=5, y=280)
        R2 = tk.Radiobutton(frame2, text="von-Mieses-Spannung", variable=sim_para.Var3, value=2, command=sel)
        R2.place(x=5, y=260)
        
        
#Modelle importieren
class Import_Modelle(GUI):
    
    ansys_init_model=""
    ansys_mnf_mod=""
    ansys_SKO_mod=""
    adams_init_model=""
    adams_mod_final=""
    adams_mod_name=""
    adams_file_name=""
    node_num=0

    def __init__(self,parent,controller):
        GUI.__init__(self,parent)
        label1=tk.Label(self.main_frame, font=("Verdana", 20), text="Import erstellter Modelle" )
        label1.pack(side="top")
        button1 = tk.Button(self.main_frame, text="ANSYS-Modell einlesen", command=lambda: import_ansys(PageOne.CWD))
        button1.pack()
        button2 = tk.Button(self.main_frame, text="Adams-Modell CMD-Datei einlesen", command=lambda: import_adams(Import_Modelle.node_num,PageOne.CWD,0))
        button2.pack()
        
#Optimierung starten
class Optimierung(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)
        label1 = tk.Label(self.main_frame, font=("Verdana", 20), text="SKO-Optimierungsschleife")
        label1.pack(side="top")
        Var1=IntVar()
        Var2=IntVar()
        Var3=IntVar()
        Var4=IntVar()
        #Checkboxes als Checkliste vor Start der Optimierung
        Cbutton1 = tk.Checkbutton(self.main_frame, text="Arbeitsverzeichnis festgelegt", variable=Var1, onvalue=1, offvalue=0)
        Cbutton1.place(x=400, y=50)
        Cbutton2 = tk.Checkbutton(self.main_frame, text="Modelle wurden erstellt und importiert", variable=Var2, onvalue=1, offvalue=0)
        Cbutton2.place(x=400,y=75)
        Cbutton3 = tk.Checkbutton(self.main_frame, text="Simulationsparameter wurden angepasst und geprüft", variable=Var3, onvalue=1, offvalue=0)
        Cbutton3.place(x=400, y=100)
        Cbutton4 = tk.Checkbutton(self.main_frame, text="ANSYS Mechanical APDL ist geöffnet und in der definierten Position", variable=Var4, onvalue=1, offvalue=0)
        Cbutton4.place(x=400, y=125)

        #Knopf um die Optimierung zu starten:
        button2 = tk.Button(self.main_frame, text="Optimierung starten", command=lambda: optimize(sim_para.stepnumber,0,sim_para.max_step,PageOne.CWD))
        button2.place(x=400, y=160)

        #DEBUG Knopf für verschiedene DEBUG-Funktionen (im finalen Programm auskommentiert)
        # button3 = tk.Button(self.main_frame, text="DEBUG", command=lambda: DEBUG(Import_Modelle.ansys_init_model))
        # button3.place(x=400 , y=400)

#Hilfefenster:
class OpenNewWindow(tk.Tk):

    def __init__(self, *args, **kwargs):

        #Eigenschaften des Pop-up-Fensters
        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.title("Hilfe")
        self.geometry("500x300")
        self.resizable(0, 0)
        #Hilfetext
        frame1 = tk.LabelFrame(main_frame, text="Willkommen!")
        frame1.pack(expand=True, fill="both")
        button1 = tk.Button(main_frame, text="Dokumentation öffnen", command=lambda:  os.startfile(MyApp.prog_path+"\\Dokumentation_Optimizer_1000-MA.pdf"))
        button1.place(x=150, y=50)
        label1 = tk.Label(frame1, font=("Verdana", 10), text="Hier finden Sie Informationen zur Nutzung des Programms:")
        label1.pack(side="top")

#=============================================================================================================================================
#Ausfürhren der Anwendung
root = MyApp()
root.title("SKO-Optimierer")
root.mainloop()