#!/usr/bin/env python
# coding: utf-8

# In[123]:


import pandas as pd

ruta = "F:/nuevo_conocimiento/CODIGO DE TESIS (MUY IMPORTANTE)/Experimentos_con_modelos_basicos/dataset_preprocesado/dataset_abstract_preprocesado.csv"

datos = pd.read_csv(ruta)
datos


# In[ ]:





# In[124]:


datos_limpios = datos['abstract_limpio'].tolist()
etiquetas = datos['categoria'].tolist()

nuevo_data = pd.DataFrame()
nuevo_data['texto'] = datos_limpios
nuevo_data['etiquetas'] = etiquetas
nuevo_data



# In[125]:


# Crear un diccionario de mapeo de etiquetas de texto a números
mapeo = {'humano': 0, 'gensim': 1, 'llama2': 2, 'llava': 3, 'llama3': 4}

# Aplicar el mapeo a la columna
nuevo_data['etiquetas_numeros'] = nuevo_data['etiquetas'].map(mapeo)
nuevo_data


# In[126]:


import matplotlib.pyplot as plt
label_count = nuevo_data['etiquetas_numeros'].value_counts(ascending=True) ## Cuenta el numero de textos que tienen asignado esa categoria
label_count


# In[127]:


label_count.plot.bar() ## grafica la cantidad de elementos que hay en cada clases de forma verticar
plt.title('frecuency of classes')
plt.show()


# In[128]:


label_count.plot.barh() ## grafica la cantidad de elementos que hay en cada clases de forma horizontal


# In[129]:


nuevo_data['Words Per Tweet'] = nuevo_data['texto'].str.split().apply(len) ## Hace un conteo del numero de palabras o tokens que hay en cada texto
nuevo_data.boxplot("Words Per Tweet", by='etiquetas_numeros') # Grafica el numeto aproximado de la longitud de los texts de cada clase. 

# ESTO ES SUPER IMPORTANTE YA QUE CON ESTO PODEMOS DEFINIR LA LONGITUD DE LOS EMBEDDINGS DE NUESTROS TRANSFORMERS, ESTO ES ALGO QUE GUARDAR MUY IMPORTANTE


# In[177]:


from transformers import AutoTokenizer
import math

#model_ckpt = "distilbert-base-uncase"
model_ckpt = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
nuevo_data

nuevo_data_1 = pd.DataFrame(index=None)
nuevo_data_1['text'] = nuevo_data['texto'].tolist()
nuevo_data_1['label'] = nuevo_data['etiquetas_numeros'].tolist()
nuevo_data_1


# In[178]:


import pandas as pd
from sklearn.model_selection import train_test_split

df_entrenamiento, df_resto = train_test_split(nuevo_data_1, test_size=0.4, random_state=42)
df_validacion, df_prueba = train_test_split(df_resto, test_size=0.5, random_state=42)


# In[179]:


from datasets import Dataset, DatasetDict
dataset_train = Dataset.from_pandas(df_entrenamiento)
dataset_validation = Dataset.from_pandas(df_validacion)
dataset_test = Dataset.from_pandas(df_prueba)


# In[180]:


# Crear el DatasetDict
dataset_dict = DatasetDict({
    'train': dataset_train,
    'validation': dataset_validation,
    'test': dataset_test
})


# In[181]:


dataset_dict


# In[182]:


def tokenize(batch):
    temp = tokenizer(batch['text'], padding=True, truncation = True)
    return temp


# In[183]:


emotion_encoded = dataset_dict.map(tokenize, batched=True, batch_size=None)


# In[184]:


emotion_encoded


# In[185]:


print(emotion_encoded['train']['text'][:1])
print(emotion_encoded['train']['label'][:1])
print(emotion_encoded['train']['input_ids'][:1])
print(emotion_encoded['train']['attention_mask'][:1])


# In[186]:


from transformers import AutoModel
import torch

model = AutoModel.from_pretrained(model_ckpt)


# In[187]:


from transformers import AutoModelForSequenceClassification


# In[188]:


num_labels = 5

device = torch.device("cuda" if torch.cuda.is_available() else 'cpu')
print(device)
model = AutoModelForSequenceClassification.from_pretrained(model_ckpt,num_labels = num_labels).to(device)


# In[189]:


from transformers import TrainingArguments


# In[190]:


batch_size = 64
model_name = "distilbert-finetuned-emotion"

training_args = TrainingArguments(output_dir = model_name,
                                 num_train_epochs=10,
                                 learning_rate = 2e-5,
                                 per_device_eval_batch_size= batch_size,
                                 per_device_train_batch_size = batch_size,
                                 weight_decay = 0.01,
                                 evaluation_strategy = 'epoch',
                                 disable_tqdm = False)


# In[144]:


from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from joblib import dump
import pickle
from sklearn.svm import SVC
import os
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_predict
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time
import pickle

def crear_directorio(nombre_carpeta):
    directorio_actual = os.getcwd()
    print("El directorio actual es:", directorio_actual)
    ruta_nueva_carpeta = os.path.join(directorio_actual, nombre_carpeta)
    # Verificar si la carpeta ya existe
    if not os.path.exists(ruta_nueva_carpeta):
        # Crear la carpeta si no existe
        os.mkdir(ruta_nueva_carpeta)
        print("Se creó la carpeta", nombre_carpeta, "en", directorio_actual)
    else:
        print("La carpeta", nombre_carpeta, "ya existe en", directorio_actual)

    ruta_modificada = ruta_nueva_carpeta.replace("\\","/")
    return ruta_modificada

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    
    exactitud = accuracy_score(labels, preds)
    precision = precision_score(labels, preds, average='weighted')
    recall = recall_score(labels, preds, average='weighted')
    f1 = f1_score(labels, preds, average='weighted')
    matriz_confusion = confusion_matrix(labels, preds)

    # Crear un mapa de calor para la matriz de confusión
    plt.figure(figsize=(8, 6))
    sns.heatmap(matriz_confusion, annot=True, fmt="d", cmap="Blues")
    plt.title('Matriz de Confusión')
    plt.xlabel('Etiquetas Predichas')
    plt.ylabel('Etiquetas Verdaderas')

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    ruta_figura_incom = crear_directorio("Bert_model_classification_10_epochs")
    ruta_figura = f"{ruta_figura_incom}/matriz_confusion_{timestamp}.png"
    plt.savefig(ruta_figura)
    print("Matriz de confusión guardada en:", ruta_figura)
    plt.show()

    return {'accuracy': exactitud,'precision':precision ,'recall':recall, 'f1':f1}


# In[145]:


from transformers import Trainer

trainer = Trainer(model = model, args= training_args,
                 compute_metrics = compute_metrics,
                 train_dataset=emotion_encoded['train'],
                 eval_dataset = emotion_encoded['validation'],
                 tokenizer=tokenizer)


# In[146]:


trainer.train()


# In[147]:


preds_outputs = trainer.predict(emotion_encoded['test'])
print(preds_outputs.metrics)


# In[151]:


print(preds_outputs.metrics)


# In[148]:


import json
resultados = preds_outputs.metrics
print(resultados)

direccion_actual = os.getcwd()
ruta_figura_incom = crear_directorio("Bert_model_classification_10_epochs")
ruta_archivo = ruta_figura_incom + "/" + "resultados_10_epochs.json"
print(ruta_archivo)
# Guardar el diccionario como JSON
with open(ruta_archivo, "w") as archivo:
    json.dump(resultados, archivo)

print("Diccionario guardado como JSON correctamente.")


# In[149]:


import numpy as np
y_preds = np.argmax(preds_outputs.predictions, axis = 1)
y_true = emotion_encoded['test'][:]['label']


# In[157]:


from sklearn.metrics import classification_report
print(classification_report(y_true,y_preds))
report_new = classification_report(y_true,y_preds,output_dict = True)


# In[159]:


import pandas as pd
report_classification = pd.DataFrame(report_new)
ruta_archivo = ruta_figura_incom + "/" + "reporte_10_epocas.csv"
report_classification.to_csv(ruta_archivo)


# In[174]:


ruta_archivo = ruta_figura_incom + "/" + "modelo_almacenado"
trainer.save_model(ruta_archivo)
print("Modelo BERT entrenado guardado correctamente en:", ruta_archivo)

## Cargar modelo entrenado
# In[176]:


import torch
from transformers import BertTokenizer
from transformers import BertForSequenceClassification

# Ruta donde guardaste el modelo entrenado
ruta_modelo_guardado = ruta_archivo

# Cargar el modelo entrenado
modelo_cargado = BertForSequenceClassification.from_pretrained(ruta_modelo_guardado)

# Ahora puedes usar 'modelo_cargado' para hacer predicciones u otras tareas

# Supongamos que tienes un texto de ejemplo para predecir
texto_ejemplo = "hola, soy david, soy ingenierio quimico"

# Tokenizar el texto de ejemplo
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
inputs = tokenizer(texto_ejemplo, return_tensors="pt")

# Pasar los datos tokenizados al modelo para hacer la predicción
with torch.no_grad():
    outputs = modelo_cargado(**inputs)

# Obtener las predicciones
predicciones = torch.argmax(outputs.logits, dim=1)

# Imprimir las predicciones
print("Predicción:", predicciones.item())

