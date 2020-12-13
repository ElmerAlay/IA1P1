import random
import math
import csv
import os
from datetime import datetime
from node import Node

class Algorithm:
    filename = ""
    criterion = 1
    selection = 1
    cant_poblacion = 20
    num_decimales = 4
    limit_i = -2
    limit_s = 2
    generation = 0

    def __init__(self, filename, criterion, selection):
        self.criterion = criterion
        self.selection = selection
        self.filename = filename

    def initPoblacion(self):
        poblacion = []

        for i in range(self.cant_poblacion):
            individuo = Node()
            genes = []
            
            for j in range(4):
                genes.append(round(random.uniform(self.limit_i, self.limit_s), self.num_decimales))

            individuo.solucion = genes
            poblacion.append(individuo)
        
        return poblacion

    def leerCSV(self):
        results = []

        with open(self.filename) as File:
            reader = csv.DictReader(File)
            for row in reader:
                results.append(row)
            
        return results
    
    def calcNote(self, results, individuo):
        notes = []

        for dictionary in results:
            nc = individuo.solucion[0]*float(dictionary['PROYECTO 1']) + individuo.solucion[1]*float(dictionary['PROYECTO 2']) + individuo.solucion[2]*float(dictionary['PROYECTO 3']) + individuo.solucion[3]*float(dictionary['PROYECTO 4'])

            notes.append({'PROYECTO 1':float(dictionary['PROYECTO 1']), 'PROYECTO 2': float(dictionary['PROYECTO 2']), 'PROYECTO 3':float(dictionary['PROYECTO 3']),'PROYECTO 4':float(dictionary['PROYECTO 4']), 'NOTA FINAL': float(dictionary['NOTA FINAL']), 'NOTA CALCULADA':nc})

        return notes
    
    def errorCuadratico(self, notes):
        fitness = 0

        for note in notes:
            fitness += pow(note['NOTA FINAL'] - note['NOTA CALCULADA'],2)

        fitness /= len(notes)

        return fitness

    def evaluarFitness(self, individuo, results):
        notes = self.calcNote(results, individuo)
        fitness = self.errorCuadratico(notes)
        
        return fitness

    def verificarCriterio(self, poblacion, generacion, results):
        result = None

        #Tiene que haber un individuo en la población que tenga un fitness menor o igual a 0.5
        if self.criterion==1:
            for individuo in poblacion:
                individuo.fitness = self.evaluarFitness(individuo, results)
                if individuo.fitness<=0.5:
                    result = True
                    break

        #Número máximo de generaciones
        if self.criterion==2:
            for individuo in poblacion:
                individuo.fitness = self.evaluarFitness(individuo, results)
            
            if generacion==5000:
                result = True

        #Que un 70% de la población tengan menos de 0.5 de valor fitness
        if self.criterion==3:
            cant = 0
            porcent = math.ceil((len(poblacion)*70)/100)
            
            for individuo in poblacion:
                individuo.fitness = self.evaluarFitness(individuo, results)
                if individuo.fitness<=0.5:
                    cant += 1
            
            if cant>=porcent:
                result = True

        return result

    def ordenar(self, poblacion):
        for x in range(self.cant_poblacion):
            for i in range(self.cant_poblacion-1):
                if poblacion[i].fitness>poblacion[i+1].fitness:
                    tmp = poblacion[i+1]
                    poblacion[i+1]=poblacion[i]
                    poblacion[i]=tmp
        
        return poblacion

    def selectParents(self, poblacion):
        betterParents = []

        if self.selection==1:   #Mejores fitness
            #Ordenamos de menor a mayor para seleccionar los mejores padres
            poblacion = self.ordenar(poblacion)
            for i in range(int(self.cant_poblacion/2)):
                betterParents.append(poblacion[i])  
        if self.selection==2:   #Tournament
            for i in range(int(self.cant_poblacion/2)):
                #Obtengo 2 elementos al azar
                option1 = random.randint(0,self.cant_poblacion-1)
                option2 = random.randint(0,self.cant_poblacion-1)

                #selecciono el que tiene el menor valor fitness
                if poblacion[option1].fitness<=poblacion[option2].fitness:
                    betterParents.append(poblacion[option1])
                else:
                    betterParents.append(poblacion[option2])
        if self.selection==3:   #random
            poblacion = self.ordenar(poblacion)
            #Obtengo un arreglo de los padres que tienen por lo menos un 65% de valor fitness aprobado
            parents = poblacion[0:math.ceil((self.cant_poblacion*65)/100)+1]
            for i in range(int(self.cant_poblacion/2)):
                #Selecciono al azar los padres
                betterParents.append(random.choice(parents))


        return betterParents

    def cruzar(self, padre1, padre2):
        hijo = []
        
        for i in range(4):
            rand = round(random.uniform(0, 1), self.num_decimales)
            if rand<=0.60:
                hijo.append(padre1.solucion[i])
            else:
                hijo.append(padre2.solucion[i])

        return hijo

    def mutar(self, solucion):
        #Genero un número aleatorio entre 0 y 1
        ran = round(random.uniform(0, 1), self.num_decimales)

        #menor a 0.5 se realiza mutación, mayor no se realiza
        if ran <= 0.5:
            for i in range(len(solucion)):
                probabilidad = round(random.uniform(0, 1), self.num_decimales)
                if probabilidad<= 0.5:
                    solucion[i]=round(random.uniform(self.limit_i, self.limit_s), self.num_decimales)

        return solucion

    def emparejar(self, parents):
        nuevaPoblacion = parents

        for i in range(int(self.cant_poblacion/2)-1):
            hijo = Node()
            hijo.solucion = self.cruzar(parents[i], parents[i+1])
            hijo.solucion = self.mutar(hijo.solucion)
            nuevaPoblacion.append(hijo)
        
        hijo = Node()
        hijo.solucion = self.cruzar(parents[0],parents[len(parents)-1])
        nuevaPoblacion.append(hijo)

        return nuevaPoblacion

    def mejorSolucionPositiva(self, arregloMejorIndividuo):
        for i in arregloMejorIndividuo:
            if i.solucion[0]>=0 and i.solucion[1]>=0 and i.solucion[2]>=0 and i.solucion[3]>=0:
                return i
        
        return arregloMejorIndividuo[0]

    def printPoblacion(self, poblacion):
        n = 0
        for individuo in poblacion:
            print('Individuo: ', individuo.solucion, ' Fitness: ', individuo.fitness)

    def execute(self):
        results = self.leerCSV()

        generacion = 0
        poblacion = self.initPoblacion()
        fin = self.verificarCriterio(poblacion, generacion, results)

        print('********** Generación ', generacion, " **********")
        self.printPoblacion(poblacion)

        while(fin==None):
            parents = self.selectParents(poblacion)
            poblacion = self.emparejar(parents)
            generacion += 1
            fin = self.verificarCriterio(poblacion, generacion, results)
            print('********** Generación ', generacion, " **********")
            self.printPoblacion(poblacion)

        arregloMejorIndividuo = self.ordenar(poblacion)
        #mejorIndividuo = arregloMejorIndividuo[0]
        mejorIndividuo = self.mejorSolucionPositiva(arregloMejorIndividuo)

        print('\n\n*************** MEJOR INDIVIDUO***************')
        print('Individuo: ', mejorIndividuo.solucion, ' Fitness: ', mejorIndividuo.fitness, ' Generacion: ', generacion)

        self.generation = generacion

        return mejorIndividuo

    def escribirArchivo(self, solucion):
        
        criterio = ""
        if self.criterion==1:
            criterio = "Un individuo tiene 0.5 o menos de valor fitness"
        if self.criterion==2:
            criterio = "5000 generaciones máximo"
        if self.criterion==3:
            criterio = "Un 70 por ciento de la población tiene 0.5 o menos de valor fitness"

        seleccion = ""
        if self.selection==1:
            seleccion = "Mejores Padres"
        if self.selection==2:
            seleccion = "Ruleta"
        if self.selection==3:
            seleccion = "Aleatorio"

        file = open("./uploads/bitacora.txt", "a")
        file.write("Fecha y Hora: " + str(datetime.now()))
        file.write("\nCSV utilizado: " + self.filename)
        file.write("\nCriterio utilizado: " + criterio)
        file.write("\nSelección de padres utilizado: " + seleccion)
        file.write("\nNúmero de generaciones: " + str(self.generation))
        file.write("\nMejor solución: [" + str(solucion[0]) + "," + str(solucion[1]) + "," + str(solucion[2]) + "," + str(solucion[3]) + "]")
        file.write("\n\n")
        file.close
        