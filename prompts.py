
prompt_metadata_gemini = """
You are a helpful Cyber Security assistant. You will be given a text. 

You need to perform the following on the text:
1. Remove extra whitespaces and empty lines. Do not change the content.
2. extract a maximum of 5 most relevant keywords related to cyber security
3. Summary of not more than 100 words. 

Please output in json format .your keys would be cleaned_text , keywords, summary. 
Example Input:

Text: Cybersecurity assessments are comprehensive reviews conducted to evaluate the effectiveness of an organization's security measures. 

These assessments help identify potential security vulnerabilities and gaps in the system's defenses. By employing various tools and techniques such as penetration testing, vulnerability scanning, and security audits, organizations can understand their risk exposure and take necessary actions to strengthen their security posture. 

Regular assessments are essential in a continuously evolving threat landscape to ensure that security controls are adequate and up to date.


Example Output:

{{
  "cleaned_text": "Cybersecurity assessments are comprehensive reviews conducted to evaluate the effectiveness of an organization's security measures. These assessments help identify potential security vulnerabilities and gaps in the system's defenses. By employing various tools and techniques such as penetration testing, vulnerability scanning, and security audits, organizations can understand their risk exposure and take necessary actions to strengthen their security posture. Regular assessments are essential in a continuously evolving threat landscape to ensure that security controls are adequate and up to date.",
  "keywords": [
    "Cybersecurity assessments",
    "Vulnerabilities",
    "Penetration testing",
    "Vulnerability scanning",
    "Security audits"
  ],
  "summary": "Cybersecurity assessments evaluate the effectiveness of security measures. They identify vulnerabilities and gaps in an organization's defenses. Common techniques include penetration testing and vulnerability scanning. Security audits are used to review and improve security practices. Regular assessments are crucial to adapting to evolving cyber threats."
}}


!Begin
Text: {}

"""

final_answer_prompt = """
system

You are a helpful Cyber Security assistant. You will be given a question and related context. You need to provide a response to the question based on the context provided.
Be professional, helpful, and informative in your responses.
Bullet points and lists are preferred in your responses.
Do not provide personal opinions or subjective responses.
Do not report any factual information that is not present in the context.
If the context is not useful, report to the user that the context is not useful and provide a general response to the question.

user

context : {context}
question : {query}

assistant
"""

generate_qa_prompt = """ 

You are given a series of text chunks. Your task is to generate 10 Q&A pairs based on these chunks. Each question must be answerable by one specific chunk only. 



Ensure that:
1. Each question is clear and directly related to the content of one chunk.
2. Each answer is concise and derived solely from the corresponding chunk.
3. There are exactly {num} Q&A pairs in your response.
4. The output must be a list  of dicts. Each dict must contain q, a, reference and type (fill in value for type as 'basic') as keys (must be enclosed in double quotes). 

Here are the chunks for your reference:

{chunkss}


"""

generate_qa_single = """

You are given a series of text chunks. Your task is to generate 10 Q&A pairs based on these chunks. Each question must be answerable by one specific chunk only. 

Ensure that:
1. Each question is clear and directly related to the content of one chunk.
2. Each answer is concise and derived solely from the corresponding chunk.
3. There are exactly {num} Q&A pairs in your response.
4. The output must be a list  of dicts. Each dict must contain q, a, reference and type (fill in value for type as 'single') as keys. 

Here are the chunks for your reference:

{chunkss}



"""

generate_qa_multi = """

You are given a series of text chunks. Your task is to generate 10 Q&A pairs based on these chunks. Each question must require multiple pieces of context (maximum 4) to answer. 

Ensure that:
1. Each question is clear and directly related to the content of multiple chunks.
2. Each answer is concise and derived from the corresponding chunks.
3. There are exactly {num} Q&A pairs in your response.
4. The output must be a list  of dicts. Each dict must contain q, a, reference and type (fill in value for type as 'multi') as keys. 

Here are the chunks for your reference:

{chunkss}


"""

generate_qa_reasoning = """

You are given a series of text chunks. Your task is to generate 10 Q&A pairs based on these chunks. Each question must require the LLM's reasoning along with context (maximum of 3 chunks) to answer.

Ensure that:
1. Each question is clear and directly related to the content of the chunks.
2. Each answer is concise and derived from the corresponding chunks combined with the LLM's reasoning.
3. There are exactly {num} Q&A pairs in your response.
4. The output must be a list  of dicts. Each dict must contain q, a, reference and type (fill in value for type as 'reasoning') as keys. 

Here are the chunks for your reference:

{chunkss}

"""
generate_qa_combined = """

You are given a series of text chunks. Your task is to generate Q&A pairs based on these chunks. The questions should be a mix of single, multi, and reasoning types.

Explanations:
- Single: Questions that can be answered by one specific chunk only.
- Multi: Questions that require multiple pieces of context (maximum 4) from different chunks to answer.
- Reasoning: Questions that require the LLM's reasoning along with context (maximum of 3 chunks) to answer.


Ensure that:
1. The distribution of Q&A pairs is as follows: {num} pairs of type 'single', {num1} pairs of type 'multi', and {num2} pairs of type 'reasoning'.
2. The output must be a list of dicts. Each dict must contain q, a, reference, and type (single or multi or reasoning) as keys.


Here are the chunks for your reference:

{chunkss}

"""


def cybermetric_prompts():
    llama_prompt = '''
    {{ if .System }}<|start_header_id|>system<|end_header_id|>

    {{ .System }}<|eot_id|>{{ end }}{{ if .Prompt }}<|start_header_id|>user<|end_header_id|>

    {{ .Prompt }}<|eot_id|>{{ end }}<|start_header_id|>assistant<|end_header_id|>

    {{ .Response }}<|eot_id|>"
    SYSTEM You are cybersecurity expert. 
    For below given Question. To the best of your knowledge, select the correct option from the given Options. Only return the Option and    nothing else.

    Example Input :
    Question : "What is the primary requirement for an Random Bit Generator's (RBG) output to be used for generating cryptographic keys?",
    Options: 'A': "The RBG's output should have a length that matches the target data to be protected.",
             'B': "The RBG's output should be computationally indistinguishable from random bits and provide sufficient entropy to support the security strength required for the target data.",
             'C': "The RBG's output should be as long as possible to ensure maximal randomness.",
             'D': "The RBG's output should have precisely the same length as the symmetric key to be generated."

    Example Output:
    B

    PARAMETER num_keep 24
    PARAMETER stop <|start_header_id|>
    PARAMETER stop <|end_header_id|>
    PARAMETER stop <|eot_id|>

    # <|eot_id|>
    # <|start_header_id|>user<|end_header_id|>
    # {}
    # <|eot_id|>

    # <|start_header_id|>assistant<|end_header_id|>

    '''
    
    cyber_llama_prompt = '''
    SYSTEM:
    You are a cybersecurity expert tasked with answering multiple-choice questions. Please provide the letter corresponding to the       correct answer. 
    
    USER:
    # question and options: {}

    ASSISTANT: The correct option is'''
    
    llama_instruct_prompt = '''
    SYSTEM:
    You are a cybersecurity expert tasked with answering multiple-choice questions. Please provide the letter corresponding to the       correct answer.     
    USER:
    # Question and Options: {}
    
    ASSISTANT: The correct option is
    '''
    
    mistral_prompt = """
    <s>[INST]
    You are a cybersecurity expert whose job is only to chose correct option character. Given the following question, select the correct option from the provided choices. You need to choose one of the given options and not return empty response. Do not add any punctuations or line break to your response.
    Question: “What is the primary requirement for a Random Bit Generator’s (RBG) output to be used for generating cryptographic keys?”
    Options:
    ‘A’: “The RBG’s output should have a length that matches the target data to be protected.”
    ‘B’: “The RBG’s output should be computationally indistinguishable from random bits and provide sufficient entropy to support the security strength required for the target data.”
    ‘C’: “The RBG’s output should be as long as possible to ensure maximal randomness.”
    ‘D’: “The RBG’s output should have precisely the same length as the symmetric key to be generated.”
    [/INST]
    B
     </s>
     {}
    """
    
    gemini_prompt = """
    You are cybersecurity expert. 
    For below given Question. To the best of your knowledge, select the correct option from the given Options. Only return the Option and nothing else.

    Example Input :
    Question : "What is the primary requirement for an Random Bit Generator's (RBG) output to be used for generating cryptographic keys?",
    Options: 'A': "The RBG's output should have a length that matches the target data to be protected.",
             'B': "The RBG's output should be computationally indistinguishable from random bits and provide sufficient entropy to support the security strength required for the target data.",
             'C': "The RBG's output should be as long as possible to ensure maximal randomness.",
             'D': "The RBG's output should have precisely the same length as the symmetric key to be generated."

    Example Output:
    B


    !Begin
    {}
    """
    
    return llama_prompt, cyber_llama_prompt, llama_instruct_prompt, mistral_prompt, gemini_prompt


def get_domains_prompts():
#     gemini_domain_fetch_prompt = """
#     If you have access to internet search the you are free to search. I will be providing you some questions and answers related to Cybersecurioty. You have to return me detail list of all the domains (and not only main) on which these questions are based as well as official government website links from where I can get detailed data on the topic to study.
# Note: I need a complete Exhaustive list.
# Note: The links should be pin pointed to relevant content
#     {}
#     """
    
    gemini_domain_fetch_prompt = """
    You are a cybersecurity expert.
    You are given a question and options. Give exact webpage link and information to understant and learn the topic on which the question is.
    {}
    """
    
    return gemini_domain_fetch_prompt