# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 16:17:57 2023
@author: josem

"""
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Comprobamos que estimulos tinen una ACC superior a 0.80 
DatosACC_global = pd.DataFrame({})

for i in range(1,53):
    # Leer el archivo

    data = pd.read_excel(f"O:/OneDrive/Documentos/PSICOLOGIA2020_24/5º_CURSO_(Granada)/TFG/Cribado_estimulos_Chema/Datos/S{i:03}_data_target.xlsx") 
    
    #Eliminamos la fila repetida de RT_1
 #   data = data.drop("RT.1", axis=1)

    # Filtramos las filas que no contienen con celdas vacías
    data = data.dropna(subset=["stim","validity","ACC","RT"])

    #Filtramos para dejar solo los ensayos validos
    data = data[data["validity"] == "Val"]

    #Filtramos por tiempo de respuesta
    data = data[data["RT"] < 1.5]
    DatosACC_global = pd.concat([DatosACC_global, data], ignore_index=True)


precision_por_estimulo = DatosACC_global.groupby('stim')['ACC'].mean()
precision_por_estimulo = precision_por_estimulo[precision_por_estimulo >= 0.80].index


del i
del data
del DatosACC_global
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##LIMPIAREMOS LOS DATOS PARA QUEDARNOS SOLO CON LOS ENSAYOS VALIDOS, LOS ACIERTOS Y LOS QUE ESTEN DENTRO DEL TIEMPO PARA VER QUÉ ESÍMULOS TEINEN RT SIMILARES
Datos_global = pd.DataFrame({})

for i in range(1,53):
    # Leer el archivo

    data = pd.read_excel(f"O:/OneDrive/Documentos/PSICOLOGIA2020_24/5º_CURSO_(Granada)/TFG/Cribado_estimulos_Chema/Datos/S{i:03}_data_target.xlsx") 
    
    #Eliminamos la fila repetida de RT_1
 #   data = data.drop("RT.1", axis=1)

    # Filtramos las filas que no contienen con celdas vacías
    data = data.dropna(subset=["stim","validity","ACC","RT"])

    #Filtramos por solo los aciertos
    data = data[data["ACC"] == 1]

    #Filtramos para dejar solo los ensayos validos
    data = data[data["validity"] == "Val"]

    #Filtramos por tiempo de respuesta
    data = data[data["RT"] < 1.5]
    
    Datos_global = pd.concat([Datos_global, data], ignore_index=True)
    
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

##IMPORTAMOS NOS NOMBRES DE LOS ESTIMULOS ASOCIADOS A SI SON CARAS O NOMBRES

code_targets = pd.read_excel("O:/OneDrive/Documentos/PSICOLOGIA2020_24/5º_CURSO_(Granada)/TFG/Cribado_estimulos_Chema/Datos/Codigo_estimulos.xlsx")

#Nos quedamos con los codigos de las caras
code_faces = code_targets[code_targets["categoria"] == "Face"]
code_faces = code_faces.drop("categoria", axis=1)

#Nos quedamos con los codigos de las nombres
code_names = code_targets[code_targets["categoria"] == "Word"]
code_names = code_names.drop("categoria", axis=1)


##CALCULAMOS LA MEDIA Y LA SD PARA LAS CARAS Y LOS NOMBRES

#Separamos los datos de Rt en funcion de si son de caras o de nombres

Datos_faces = Datos_global[Datos_global['stim'].isin(code_faces['nombre_stim'])]
mean_RT_faces = Datos_faces['RT'].mean()
sd_RT_faces = Datos_faces['RT'].std()
Mean_Rt_stim_faces = Datos_faces.groupby('stim').RT.mean().reset_index()
Mode_gender_faces = Datos_faces.groupby('stim').gender.apply(lambda x: x.mode()[0]).reset_index()
Mean_Rt_stim_faces = Mean_Rt_stim_faces.merge(Mode_gender_faces, on='stim')

Datos_names = Datos_global[Datos_global['stim'].isin(code_names['nombre_stim'])]
mean_RT_names = Datos_names['RT'].mean()
sd_RT_names = Datos_names['RT'].std()
Mean_Rt_stim_names = Datos_names.groupby('stim').RT.mean().reset_index()
Mode_gender_names = Datos_names.groupby('stim').gender.apply(lambda x: x.mode()[0]).reset_index()
Mean_Rt_stim_names = Mean_Rt_stim_names.merge(Mode_gender_names, on='stim')




#-------------------------------------------------------------------------------------------------------------------------------------------------------------

num_samples = 1000000  # Número de submuestras aleatorias a tomar
best_difference = float('inf')  # Inicializar la mejor diferencia a infinito
best_subsample_faces = pd.DataFrame({})
best_subsample_names = pd.DataFrame({})

for i in range(num_samples):
    print(i)
    # Seleccionar 8 estímulos de cada género para faces
    subsample_df1_fem = Mean_Rt_stim_faces[Mean_Rt_stim_faces['gender'] == 'Fem'].sample(8)
    subsample_df1_mas = Mean_Rt_stim_faces[Mean_Rt_stim_faces['gender'] == 'Mas'].sample(8)
    subsample_df1 = pd.concat([subsample_df1_fem, subsample_df1_mas])

    # Seleccionar 8 estímulos de cada género para names
    subsample_df2_fem = Mean_Rt_stim_names[Mean_Rt_stim_names['gender'] == 'Fem'].sample(8)
    subsample_df2_mas = Mean_Rt_stim_names[Mean_Rt_stim_names['gender'] == 'Mas'].sample(8)
    subsample_df2 = pd.concat([subsample_df2_fem, subsample_df2_mas])
    
    # Calcular media y desviación estándar para ambas submuestras
    mean_df1, std_df1 = subsample_df1['RT'].mean(), subsample_df1['RT'].std()
    mean_df2, std_df2 = subsample_df2['RT'].mean(), subsample_df2['RT'].std()
    
    # Calcular la diferencia entre medias y desviaciones estándar
    mean_diff = abs(mean_df1 - mean_df2)
    std_diff = abs(std_df1 - std_df2)
    total_diff = mean_diff + std_diff  # Medida para determinar las mejores submuestras
    
    if total_diff < best_difference:
        best_difference = total_diff
        best_subsample_faces = subsample_df1
        best_subsample_names = subsample_df2
        print("nuevo mejor")



#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




# Realizar la prueba t
t_stat, p_valor = ttest_ind(best_subsample_faces['RT'], best_subsample_names['RT'])

print(f"P-valor: {p_valor}")
print(f"Estadístico t: {t_stat}")



#if p_valor >= 0.05:
#    best_subsample_faces.to_excel('C:/Users/josem/OneDrive/Documentos/PSICOLOGIA2020_24/5º_CURSO_(Granada)/TFG/Cribado_estimulos_Chema/Datos/estimulos_caras_seleccionados.xlsx', engine='openpyxl', index=False)
#    best_subsample_names.to_excel('C:/Users/josem/OneDrive/Documentos/PSICOLOGIA2020_24/5º_CURSO_(Granada)/TFG/Cribado_estimulos_Chema/Datos/estimulos_nombres_seleccionados.xlsx', engine='openpyxl', index=False)

    






















   