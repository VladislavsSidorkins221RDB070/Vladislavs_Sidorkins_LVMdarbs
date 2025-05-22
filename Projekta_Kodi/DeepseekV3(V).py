import pandas as pd
import requests
import time

API_URL = "https://api.deepseek.com"
API_KEY = "api_atslēga" 
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

PROMPT_TEMPLATE = """
Lūdzu, atbildi uz šo jautājumu, izvēloties vienu no piedāvātajiem atbilžu variantiem.
Jautājums: {question}
Atbilžu varianti:
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}
Atbildi tikai ar burtu (A, B, C vai D) bez papildus paskaidrojumiem.
"""

def iegut_atbildi(jautajums, izveles):

    try:
        prompts = PROMPT_TEMPLATE.format(
            question=jautajums,
            option_a=izveles[0],
            option_b=izveles[1],
            option_c=izveles[2],
            option_d=izveles[3]
        )
        
        dati = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompts}],
            "temperature": 0.0,  
            "max_tokens": 1      
        }


        atbilde = requests.post(API_URL, json=dati, headers=HEADERS)
        atbilde.raise_for_status()
        

        modela_atbilde = atbilde.json()["choices"][0]["message"]["content"].strip().upper()
        

        if modela_atbilde in ['A', 'B', 'C', 'D']:
            return modela_atbilde
        return "X"  
    
    except Exception as kļūda:
        print(f"API pieprasījuma kļūda: {kļūda}")
        return "E"  

def apstrada_testu(ievada_fails, izvada_fails):


    dati = pd.read_csv(ievada_fails)
    

    dati['Modela_Atbilde'] = ""
    dati['Vai_Pareiza'] = ""
    

    for indekss, rinda in dati.iterrows():
        jautajums = rinda[0]  
        varianti = [
            str(rinda[1]),  
            str(rinda[2]),  
            str(rinda[3]),  
            str(rinda[4])   
        ]
        pareiza_atbilde = str(rinda[5]).strip().upper()  

        atbilde = iegut_atbildi(jautajums, varianti)
        

        dati.at[indekss, 'Modela_Atbilde'] = atbilde

        dati.at[indekss, 'Vai_Pareiza'] = "Jā" if atbilde == pareiza_atbilde else "Nē"
        
        print(f"Pabeigts {indekss+1}/{len(dati)}: {jautajums[:30]}...")
        time.sleep(1)  
    

    dati.to_csv(izvada_fails, index=False)
    print(f"Rezultāti veiksmīgi saglabāti: {izvada_fails}")

if __name__ == "__main__":
    apstrada_testu("jautajumi.csv", "rezultati.csv")