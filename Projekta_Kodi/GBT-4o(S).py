import csv
import openai

openai.api_key = "OPENAI_API_ATSLĒGA"

def ask_chatgpt(question, options):
    """
    Nosūta jautājumu un atbilžu variantus ChatGPT ar jauno promptu latviešu valodā.
    Atgriež atbildes burtu (A, B, C vai D).
    """
    prompt = (
        "Tas nozīmē, ka, izvēloties atbildi, modelim jāņem vērā ne tikai jautājuma nozīme, bet arī tas, "
        "kā tas ir formulēts un kas varētu būt paslēpts formulējumā vai piezīmēs.\n\n"
        f"{question}\n"
        f"{options}\n"
        "Atbilde (A, B, C vai D):"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu esi palīdzīgs modelis, kas izvēlas pareizās atbildes uz testu jautājumiem, rūpīgi analizējot formulējumus un slēptos mājienus."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0,
        )
        answer = response['choices'][0]['message']['content'].strip().upper()
        if answer and answer[0] in ['A', 'B', 'C', 'D']:
            return answer[0]
        else:
            return ""
    except Exception as e:
        print(f"API kļūda: {e}")
        return ""

def process_csv(input_file, output_file):
    """
    Nolasa CSV failu, nosūta jautājumus uz GPT, saglabā atbildes un izveido jaunu failu ar papildus kolonnām.
    """
    with open(input_file, encoding='utf-8') as csvfile:
        reader = list(csv.reader(csvfile))
        header = reader[0]
        
        header.append("GPT_atbilde")
        header.append("Pareizi?")

        data = reader[1:]

    for row in data:
        question = row[0]
        options_text = f"A) {row[1]}\nB) {row[2]}\nC) {row[3]}\nD) {row[4]}"
        gpt_answer = ask_chatgpt(question, options_text)
        row.append(gpt_answer)
        row.append("")

    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile_out:
        writer = csv.writer(csvfile_out)
        writer.writerow(header)
        writer.writerows(data)

if __name__ == "__main__":
    process_csv("jautajumi.csv", "jautajumi_ar_atbildem.csv")
    print("Apstrāde pabeigta! Rezultāts saglabāts: jautajumi_ar_atbildem.csv")
