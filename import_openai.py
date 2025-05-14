import openai
openai.api_key = "ysk-proj-if42SoA46kht-z8TnOtuHtrawz6_f0ZKsDWcIZmezRUlDCtTuSXulNqdFm6Sty4Cm6DEd1zsaeT3BlbkFJssQDbwVfad02DKoe9k3r_rR3sX3rZJz8TEfZym3sXKYBbrUyeytqtJMaQK66rJjVAzfzKS5uQA"

try:
    res = openai.ChatCompletion.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(res.choices[0].message["content"])
except Exception as e:
    print("❌", e)
