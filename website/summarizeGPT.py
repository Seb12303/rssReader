from openai import OpenAI
api_key_1 = 'sk-proj-wZZKksNo_Wq1F4Bj_kInlSmreRIAcuE-CV0Ql3gP4Q7o38Iunr5GEQIuAl87OPhW-REMOVED_SECRET'

client = OpenAI(api_key=api_key_1)

def getSummary(text):
    
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "You summerize text. Only give the summary and nothing else. Summarize to simple points. USE THE SAME LANGUAGE AS THE TEXT YOU ARE GIVEN."
            }
        ]
        },
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": text
            }
        ]
        }
    ],
    response_format={
        "type": "text"
    },
    temperature=1,
    max_completion_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response.choices[0].message.content
if __name__ == "__main__":
    print(getSummary('''
Under tirsdagens pressekonferanse før den avgjørende Champions League-kampen mot Club Brügge bekrefter Pep Guardiola at Oscar Bobb trolig er tilbake for de lyseblå.

– Alle som var med mot Chelsea på lørdag er tilgjengelig, i tillegg til at Oscar Bobb trolig er tilbake, sier Guardiola på pressekonferansen.

Bobb pådro seg et beinbrudd på trening i august. Siden har han ikke vært å se på banen for verken Manchester City eller landslaget.

Oslo-gutten har spilt 27 kamper for Manchester City, der han har scoret to mål og har tre målgivende pasninger. Det store høydepunktet i nordmannens Manchester City-karriere er nok hans høydramatiske matchvinner-scoring borte mot Newcastle forrige sesong.

Se målet som også ble kåret til månedens mål under:

Guardiola vil samtidig ikke avskrive at situasjonen før onsdagens kamp er som den er.

- Vi må vinne kampen. Hvis ikke er vi ute, sier spanjolen tydelig på hva som gjelder for Manchester City i onsdagens kamp.
'''))