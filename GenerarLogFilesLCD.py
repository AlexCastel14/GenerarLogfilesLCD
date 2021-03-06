import tkinter as tk
import tkinter.messagebox
import os
import datetime

def center(window):                                                             #Centra la ventana en la pantalla
       window.update_idletasks()
       x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
       y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
       window.geometry('+{}+{}'.format(x, y))

def CalcularEndtime(time,reporteHTMLPath):                                          #Calcula el la hora en que se terminó la prueba
    splittedTime=time.split(":")
    hour=int(splittedTime[0])
    min=int(splittedTime[1])
    sec=int(splittedTime[2])
    reporteHTML=open(reporteHTMLPath,"r",errors='ignore')
    i=0
    for line in reporteHTML:
        i=i+1
        if i==113:
            splittedExecutionTime=line[7:].split(".")
            ExecutionTime=splittedExecutionTime[0]
            sec=sec+int(ExecutionTime)
            if sec>59:
                addMin=sec//60
                min=min+addMin
                sec=sec-(60*addMin)
                if min>59:
                    hour=hour+1
                    min=min-60
                    if hour>23:
                        hour=0
            EndTime=str(hour)+":"+str(min)+":"+str(sec)
            return(EndTime)


def CrearArchivo(NumSerie,destino,versionNoAN,day,month,year,time,reporteHTMLPath): #Crea logfile para empaque
    sn=NumSerie
    filePath=destino+sn+"_PASS.txt"
    version="AN"+versionNoAN
    file=open(filePath,"w")
    file.write("#\n")
    file.write(".version 2\n")
    file.write("2 "+ sn + "\n")
    file.write("4 "+ version + "\n")
    file.write("5 FT\n")
    file.write("6 38\n")
    file.write("7 55\n")
    file.write("8 FT_LCD_2\n")
    file.write("13 " + day + "." + month + "." + year + "\n")
    file.write("14 "+ time +"\n")
    file.write("16 PASS\n")
    file.write("17 "+ version + "\n")
    file.write("18 "+ sn + "\n")
    file.write("19 " + day + "." + month + "." + year + "\n")
    EndTime=CalcularEndtime(time,reporteHTMLPath)
    file.write("20 " + EndTime + "\n")
    file.write("32 FCT")
    now=datetime.datetime.now()
    logfile=open("log.txt","a")
    logfile.write(NumSerie + " : "+ reporteHTMLPath + " : " + str(now) + "\n")
    tk.messagebox.showinfo("Reporte Generado", "El reporte ha sido generado con exito!")
    serialEntry.delete(0,len(NumSerie))

def check():                             #Busca y lee reportes buscando un pass
    print("-------------------  Buscando registo...  ---------------------")
    pathFile=open("Path.txt","r")                                               #Abre path.txt file
    for line in pathFile:
        if line.startswith("Origen: "):
            x=line.strip()
            initial_dir=x[8:]
        if line.startswith("Destino: "):
            y=line.strip()
            destino=y[9:]
    NumSerie=serialEntry.get()
    filename="LcdMain_Report[" + NumSerie
    status=0                                                                    #STATUS 0 SIN REGISTRO,  1 PASS, 2 FAIL
    TestDate=False
    TestTime=False
    PNstatus=False
    Serialstatus=False
    oswalkiterations=0
    totalfiles={}
    for root, dirs, files in os.walk(initial_dir):
        for fileC in files:
            totalfiles[fileC]=os.path.abspath(os.path.join(root, fileC))
    for name in totalfiles:
        extension=name.split(".")[1]
        if name.startswith(filename) and extension == "html":
            versionNoAN=name[15:23]
            reporteHTMLPath=totalfiles.get(name)
            print("Reporte Encontrado en : " + reporteHTMLPath)
            reporteHTML=open(reporteHTMLPath,"r",errors='ignore')
            i=0
            for line in reporteHTML:
                i=i+1
                if line.startswith("<TD><B>Passed"):                        #Obtiene el Pass del reporte y actualiza status 
                    print("Passed")
                    status=1
                if line.startswith("<TD><B>Failed"):                        #Verifica Fail y actualiza status
                    print("Failed")
                    status=2
                if status==1:
                    if line.startswith("<td> Model Number:"):               #Verifica que tenga el modelo guardado en la tarjeta
                        splitedLinePN=line.split()
                        PN=splitedLinePN[3]
                        if PN=="</td>":
                            PNstatus=False
                        else:
                            PNstatus=True
                    if line.startswith("<td> Serial Number:"):              #Verifica que tenga el serial guardado en la tarjeta
                        splitedLineSerial=line.split()
                        Serial=splitedLineSerial[3]
                        if Serial=="</td>":
                            Serialstatus=False
                        else:
                            Serialstatus=True
                    if i==97:                                               #Obtiene la Fecha de Prueba
                        splittedLine=line.split()
                        date=splittedLine[1]
                        splittedDate=date.split("/")
                        if not len(splittedDate)==3:
                            splittedDate=date.split("-")
                        day=splittedDate[1]
                        month=splittedDate[0]
                        year=splittedDate[2]
                        TestDate=True
                    if i==105:                                              #Obtiene Hora de Prueba
                        splittedLine=line.split()
                        time=splittedLine[1]
                        splittedTime=time.split(":")
                        hour=splittedTime[0]
                        hour=int(hour)
                        if splittedLine[2]=="PM" and hour<12:
                            hour=hour+12
                            time=str(hour)+":"+splittedTime[1]+":"+splittedTime[2]
                        TestTime=True
                    #if TestDate==True and status==1 and TestTime==True and PNstatus==True and Serialstatus==True:
                    if TestDate==True and status==1 and TestTime==True:
                        CrearArchivo(NumSerie,destino,versionNoAN,day,month,year,time,reporteHTMLPath)
                        return
                    if TestDate==True and status==1 and TestTime==True and PNstatus==False and Serialstatus==False:
                        tk.messagebox.showwarning("Pieza sin datos","Pieza sin datos de GE")
                        serialEntry.delete(0,len(NumSerie))
                        return


    if status==0:
        print("Sin registro")
        tk.messagebox.showerror("Sin Registro","La tarjeta no tiene registro de FT")
        serialEntry.delete(0,len(NumSerie))
    if status==2:
        tk.messagebox.showerror("Fail","La tarjeta falló en FT")
        print("La tarjeta falló")
        serialEntry.delete(0,len(NumSerie))

window=tk.Tk()                                                                  #Crea ventana principal
window.title("Generar Logfiles LCD")
window.resizable(0,0)
window.geometry("450x140")
window.iconphoto(True, tk.PhotoImage(file="melecs1.png"))
texto=tk.Label(window,text="Introduce un numero de serie:", font=16)
texto.pack()
texto.config(pady=20)
serialEntry=tk.Entry(window, font=16)
serialEntry.pack()
serialEntry.focus()
serialEntry.bind("<Return>", lambda _: check())
center(window)

window.mainloop()