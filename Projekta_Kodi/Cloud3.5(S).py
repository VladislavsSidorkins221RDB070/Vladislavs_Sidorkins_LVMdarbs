import os
import csv
import json
import anthropic
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class ClaudeCSVProcessor:
    def __init__(self, api_key=None):
        """
        Inicializē Claude API klientu
        
        :param api_key: API atslēga Claude piekļuvei. Ja None, tiks izmantota atslēga no ANTHROPIC_API_KEY
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API atslēga nav norādīta! Iestatiet ANTHROPIC_API_KEY vai nododiet atslēgu konstruktoram.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.current_file = None
    
    def load_csv(self, file_path):
        """
        Ielādē CSV failu un atgriež to kā pandas DataFrame
        
        :param file_path: Ceļš līdz CSV failam
        :return: DataFrame ar datiem
        """
        try:
            self.current_file = file_path
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"Kļūda ielādējot CSV failu: {e}")
            raise
    
    def ask_claude(self, question, options, model="claude-3-7-sonnet-20250219"):
        """
        Nosūta pieprasījumu Claude API un saņem atbildi
        
        :param question: Jautājums
        :param options: Atbilžu varianti (A-D)
        :param model: Claude modelis, ko izmantot
        :return: Claude atbilde (A, B, C vai D)
        """
        full_prompt = f"""Lūdzu, atbildi uz šo jautājumu, izvēloties vienu no piedāvātajiem atbilžu variantiem.

Svarīgi: Tas nozīmē, ka, izvēloties atbildi, tev jāņem vērā ne tikai jautājuma nozīme, bet arī tas, kā tas ir formulēts un kas varētu būt paslēpts formulējumā vai piezīmēs. Pievērs uzmanību niansēm un zemtekstam.
        
Jautājums: {question}

Atbilžu varianti:
A: {options['A']}
B: {options['B']}
C: {options['C']}
D: {options['D']}

Lūdzu, rūpīgi izanalizē jautājumu un visus atbilžu variantus. Pievērs uzmanību formulējumam, niansēm un iespējamām slēptām norādēm.
Atbildi tikai ar burtu (A, B, C vai D), kas apzīmē pareizo atbildi."""
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            answer = response.content[0].text.strip()
            
            for letter in ['A', 'B', 'C', 'D']:
                if letter in answer:
                    return letter
            
            return answer
        except Exception as e:
            print(f"Kļūda piekļūstot Claude API: {e}")
            return f"Kļūda: {str(e)}"
    
    def process_quiz_csv(self, file_path):
        """
        Apstrādā viktorīnas CSV failu, kuram ir jautājumi un atbilžu varianti
        
        :param file_path: Ceļš līdz CSV failam
        :return: DataFrame ar pievienotām Claude atbildēm
        """
        df = self.load_csv(file_path)

        expected_columns = 6  
        if len(df.columns) < expected_columns:
            raise ValueError(f"CSV failam vajadzētu būt vismaz {expected_columns} kolonnām")
        
        if df.columns[0] == '0' or df.columns[0].isdigit():
            df.columns = ['Jautājums', 'A', 'B', 'C', 'D', 'Pareizā_atbilde'] + list(df.columns[6:])
        
        df['Claude_atbilde'] = None
        
        df['Vērtējums'] = None
        
        for idx, row in df.iterrows():
            question = row['Jautājums']
            options = {
                'A': row['A'],
                'B': row['B'],
                'C': row['C'],
                'D': row['D']
            }
            
            claude_answer = self.ask_claude(question, options)
            
            df.at[idx, 'Claude_atbilde'] = claude_answer
            
            print(f"Apstrādāts jautājums {idx+1}/{len(df)}: Claude atbilde: {claude_answer}")
        
        return df
    
    def save_results(self, df, output_path=None):

        if output_path is None:
            base_name, ext = os.path.splitext(self.current_file)
            output_path = f"{base_name}_ar_atbildēm{ext}"
        
        df.to_csv(output_path, index=False)
        print(f"Rezultāti saglabāti {output_path}")
        return output_path



if __name__ == "__main__":

    processor = ClaudeCSVProcessor()
    

    file_path = "jautajumi.csv"
   
    results = processor.process_quiz_csv(file_path)
    
    output_file = processor.save_results(results)
