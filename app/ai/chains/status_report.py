from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from typing import List
from app.models.task import Task
import os
from app.ai.chains.base import with_fallback
from app.core.cache import cache_response

STATUS_REPORT_TEMPLATE = """
Du er en projektleder der skal generere en daglig statusrapport.
Baseret på følgende opgaver, generer en koncis men informativ statusopdatering:

Opgaver:
{tasks}

Generer en rapport med følgende sektioner:
1. Overordnet status
2. Fremskridt i dag
3. Blokeringer/Udfordringer
4. Næste skridt

Hold rapporten professionel og fokuseret på de vigtigste punkter.
"""

FALLBACK_TEMPLATE = """
Status Rapport (Fallback Version)

1. Overordnet status:
   Kunne ikke nå AI-model, viser basal statistik

2. Fremskridt:
   - Aktive opgaver: {active_count}
   - Afsluttede opgaver: {done_count}

3. Næste skridt:
   Se individuelle opgavedetaljer for mere information
"""

class StatusReportChain:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.5,
            model_name="gpt-3.5-turbo",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.prompt = PromptTemplate(
            template=STATUS_REPORT_TEMPLATE,
            input_variables=["tasks"]
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def format_tasks(self, tasks: List[Task]) -> str:
        formatted_tasks = []
        for task in tasks:
            task_str = (
                f"- {task.title} (Priority: {task.priority.value}, "
                f"Status: {task.status.value})\n"
                f"  Beskrivelse: {task.description or 'N/A'}\n"
                f"  Deadline: {task.deadline.strftime('%Y-%m-%d') if task.deadline else 'N/A'}"
            )
            formatted_tasks.append(task_str)
        return "\n".join(formatted_tasks)

    @cache_response(expire_time=900)
    @with_fallback(fallback_value=None)  # Vi håndterer fallback i metoden selv
    async def generate_status_report(self, tasks: List[Task]) -> str:
        try:
            formatted_tasks = self.format_tasks(tasks)
            report = await self.chain.arun(tasks=formatted_tasks)
            return report
        except Exception as e:
            # Hvis AI fejler, lav en basal rapport
            active_count = len([t for t in tasks if t.status != "done"])
            done_count = len([t for t in tasks if t.status == "done"])
            return FALLBACK_TEMPLATE.format(
                active_count=active_count,
                done_count=done_count
            ) 