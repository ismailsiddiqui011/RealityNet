from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
from prompts import SYSTEM_PROMPTS
import yaml

class RealityNet:
    def __init__(self, tolerance_mode = 'balanced'):
        with open("models_configs.yaml", "r") as file:
            config = yaml.safe_load(file)

        context_window = config['context_window']
        llm_model = config['llm_model']
        verifier_model = config['verifier_model']
        debator_model = config['debator_model']
        summarizer_model = config['summarizer_model']
        judge_model = config['judge_model']

        self.llm = Ollama(model=llm_model, request_timeout=60.0, context_window = context_window)
        self.verifer = Ollama(model=verifier_model, temperature=0.2, request_timeout=60.0, context_window = context_window)
        self.debator = Ollama(model=debator_model, request_timeout=60.0, temperature=0.5, context_window = context_window)
        self.summarizer = Ollama(model=summarizer_model, request_timeout=60.0, temperature=0.3, context_window = context_window)
        self.judge = Ollama(model=judge_model, request_timeout=60.0, temperature=0.1, context_window=context_window)
        self.tolerance_mode = tolerance_mode

    def generate_answer(self, question:str):
        system_prompt = SYSTEM_PROMPTS['llm_real']
        messages = [ChatMessage(role="user", content=f"Instructions: {system_prompt} \n  {question}")]
        response = self.llm.chat(messages)
        llm_answer = response.message.content
        self.llm_answer = llm_answer
        return llm_answer
    
    def generate_verification(self, llm_answer:str):
        system_prompt = SYSTEM_PROMPTS["verifier"]
        messages = [ChatMessage(role="user", content=f"Instructions: {system_prompt} \n {llm_answer}")]
        response = self.verifer.chat(messages)
        verifier_answer = response.message.content
        self.verifier_answer = verifier_answer
        return verifier_answer
    
    def generate_debate(self, llm_answer:str):
        system_prompt = SYSTEM_PROMPTS["debator"]
        messages = [ChatMessage(role="system", content=system_prompt), ChatMessage(role="user", content=f"Instructions: {system_prompt} \n {llm_answer}")]
        response = self.debator.chat(messages)
        debator_answer = response.message.content
        self.debator_answer = debator_answer
        return debator_answer
    
    def generate_summary(self, verifer_answer:str, debator_answer:str):
        system_prompt = SYSTEM_PROMPTS["summarizer"]
        messages = [ChatMessage(role="system", content=system_prompt),
                     ChatMessage(role="user", content=f"Instructions: {system_prompt} \n factual existence : \n {verifer_answer} \n logical consistency: \n {debator_answer}")]
        response = self.summarizer.chat(messages)
        summarizer_answer = response.message.content
        self.summarizer_answer = summarizer_answer
        return summarizer_answer
    
    def decide_label(self, real_score, fake_score):
        if self.tolerance_mode == 'hard':
            return "REAL" if real_score > fake_score else "FAKE"

        elif self.tolerance_mode == 'balanced':
            # Allow minor errors: if Real% is at least 10% higher than Fake%, call it Real
            if real_score - fake_score >= 10:
                return "REAL"
            elif fake_score - real_score >= 10:
                return "FAKE"
            else:
                return "UNCERTAIN"

        elif self.tolerance_mode == 'soft':
            # Very forgiving: even if Real% slightly higher, call it Real
            if real_score >= fake_score:
                return "REAL"
            else:
                return "FAKE"

        else:
            raise ValueError(f"Unknown tolerance mode: {self.tolerance_mode}")

    
    def judge_flow(self, question:str):
        system_prompt = SYSTEM_PROMPTS['judge']
        print('Generating the LLM Answer...')
        llm_answer = self.generate_answer(question)
        print('Verifing the LLM Answer...')
        verifier_answer = self.generate_verification(llm_answer)
        print('Debating on LLM Answer...')
        debator_answer = self.generate_debate(llm_answer)
        print('Summarizing the critical points...')
        summarizer_answer = self.generate_summary(verifier_answer, debator_answer)        
        print('Giving verdict on the LLM answer...')
        messages = [ChatMessage(role="user", content=f"Instructions : {system_prompt} \n critical points: \n {summarizer_answer}")]
        response = self.judge.chat(messages)
        system_prompt = SYSTEM_PROMPTS['judge']

        messages = [ChatMessage(role="user", content=f"Instructions : {system_prompt} \n critical points: \n {summarizer_answer}")]
        response = self.judge.chat(messages)
        judge_answer = response.message.content

        try:
            real_score = int(judge_answer.split("Real:")[1].split("%")[0].strip())
            fake_score = int(judge_answer.split("Fake:")[1].split("%")[0].strip())
        except Exception as e:
            print(f"Error parsing judge response: {e}")
            real_score = fake_score = -1

        final_decision = self.decide_label(real_score, fake_score)

        return llm_answer, judge_answer, final_decision