import pandas as pd
import requests
import time

API_URL = "https://api.deepseek.com"
API_KEY = "api_atslēga" 
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

DETALIZETS_PROMPTS = """
Tas nozīmē, ka, izvēloties atbildi, Tev jāņem vērā ne tikai jautājuma nozīme, 
bet arī tas, kā tas ir formulēts un kas varētu būt paslēpts formulējumā vai piezīmēs.

Analizējiet šo jautājumu un atbilžu variantus ļoti rūpīgi:

Jautājums: {jautajums}
Atbilžu varianti:
A) {a}
B) {b}
C) {c}
D) {d}

Uzmanīgi apsveriet:
1. Jautājuma formulējuma nianses
2. Iespējamos slēptos mācību elementus
3. Kontekstuālās mājienas
4. Gramatiskās un loģiskās struktūras

Atbildi tikai ar vienu burtu (A, B, C vai D) - izvēlēto atbildes variantu.
"""

def iegut_detalizetu_atbildi(jautajums, varianti):

    try:

        prompts = DETALIZETS_PROMPTS.format(
            jautajums=jautajums,
            a=varianti[0],
            b=varianti[1],
            c=varianti[2],
            d=varianti[3]
        )
        
        pieprasijums = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompts}],
            "temperature": 0.3,  
            "max_tokens": 1,     
            "top_p": 0.9        
        }


        atbilde = requests.post(API_URL, json=pieprasijums, headers=HEADERS)
        atbilde.raise_for_status()

        modela_atbilde = atbilde.json()["choices"][0]["message"]["content"].strip().upper()
        

        if modela_atbilde in ['A', 'B', 'C', 'D']:
            return modela_atbilde
        return "X"  
    
    except Exception as kļūda:
        print(f"API kļūda: {kļūda}")
        return "E"  

def apstrada_detalizeto_testu(ievada_fails, izvada_fails):


    testa_dati = pd.read_csv(ievada_fails, encoding='utf-8')
    

    testa_dati['Detalizeta_Atbilde'] = ""
    testa_dati['Pareiziba'] = ""
    testa_dati['Analizes_Piezimes'] = ""
    
    for indekss, rinda in testa_dati.iterrows():

        jautajums = str(rinda[0])
        varianti = [str(rinda[i]) for i in range(1,5)]
        pareiza_atbilde = str(rinda[5]).strip().upper()
        

        atbilde = iegut_detalizetu_atbildi(jautajums, varianti)
        

        testa_dati.at[indekss, 'Detalizeta_Atbilde'] = atbilde
        testa_dati.at[indekss, 'Pareiziba'] = "Jā" if atbilde == pareiza_atbilde else "Nē"
        

        if atbilde != pareiza_atbilde and atbilde in ['A','B','C','D']:
            testa_dati.at[indekss, 'Analizes_Piezimes'] = "Iespējama jautājuma neskaidrība"
        
        print(f"Apstrādāts {indekss+1}/{len(testa_dati)}: {jautajums[:30]}...")
        time.sleep(1.5)  
    
    testa_dati.to_csv(izvada_fails, index=False, encoding='utf-8')
    print(f"Rezultāti saglabāti: {izvada_fails}")

if __name__ == "__main__":
    apstrada_detalizeto_testu(
        ievada_fails="detalizeti_jautajumi.csv",
        izvada_fails="detalizeti_rezultati.csv"
    )