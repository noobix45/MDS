import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_name = "gpt-4o-mini"
deployment = "task-priority-ai"

subscription_key = os.getenv("OPENAI_API_KEY")
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

def sort_tasks_with_ai(task_list):
    task_info = "\n".join([
        f"Task {task.id_task}: {task.titlu} | importanta: {task.importanta} | deadline: {task.deadline} | repetitiv: {task.repetitiv} | zile: {task.days_to_do}"
        for task in task_list
    ])

    content = f"""Ai următoarele taskuri:\n{task_info}\n
        Pentru fiecare task, atribuie un scor de prioritate între 0 și 1, unde 1 înseamnă foarte important și 0 foarte puțin important.
        Răspunde în formatul:
        Task <id_task>: <scor>
        Păstrează exact ID-urile și răspunde doar cu lista, fără explicații."""

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system",
             "content": "Ești un asistent care ajută la prioritizarea taskurilor pentru utilizatori."},
            {"role": "user", "content": content},
        ],
        temperature=0.7,
    )

    raw_output = response.choices[0].message.content
    print("Răspuns de la OpenAI:", raw_output)

    #outputul un dict
    priority_scores = {}
    for line in raw_output.strip().split("\n"):
        if ":" in line:
            task_str, score = line.split(":", 1)
            try:
                task_id = int(task_str.split()[1])  # Extragerea ID-ului taskului
                priority_scores[task_id] = float(score.strip())  # Salvez scorul pentru task_id
            except ValueError:
                continue

    return priority_scores
