# modules/m1_langchain_llama/chain_builder.py
"""LangChain chain builders for various use cases."""

from typing import Optional, List
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from transformers import pipeline
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config


class ChainBuilder:
    """Builds LangChain chains for different tasks."""
    
    def __init__(self, model, tokenizer, config=None):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config or get_config()
        self.llm = self._create_hf_pipeline()
        
    def _create_hf_pipeline(self) -> HuggingFacePipeline:
        """Create HuggingFace pipeline for LangChain."""
        pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=True,
            return_full_text=False
        )
        return HuggingFacePipeline(pipeline=pipe)
    
    def create_qa_chain(self):
        """Create a simple Q&A chain using LCEL."""
        template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        prompt = PromptTemplate(
            input_variables=["system_prompt", "question"],
            template=template
        )
        
        # LCEL chain
        chain = prompt | self.llm | StrOutputParser()
        return chain
    
    def create_rag_chain(self, retriever):
        """Create a RAG chain with retrieval."""
        template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert academic research assistant. Answer the question based on the provided context from research papers. If the context doesn't contain relevant information, say so clearly.

Context from research papers:
{context}<|eot_id|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )
        
        def format_docs(docs):
            return "\n\n---\n\n".join(
                f"[Source: {doc.metadata.get('title', 'Unknown')}]\n{doc.page_content}" 
                for doc in docs
            )
        
        # LCEL chain
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
    def create_comparison_chain(self):
        """Create chain for comparing model outputs."""
        template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are evaluating two model responses to the same question. Analyze which response is better in terms of accuracy, relevance, and completeness.<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: {question}

Response A (Base Model):
{response_a}

Response B (Fine-tuned Model):
{response_b}

Provide a detailed comparison and declare a winner.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        prompt = PromptTemplate(
            input_variables=["question", "response_a", "response_b"],
            template=template
        )
        
        # LCEL chain
        chain = prompt | self.llm | StrOutputParser()
        return chain


# Convenience functions
def create_qa_chain(model, tokenizer, config=None):
    builder = ChainBuilder(model, tokenizer, config)
    return builder.create_qa_chain()

def create_rag_chain(model, tokenizer, retriever, config=None):
    builder = ChainBuilder(model, tokenizer, config)
    return builder.create_rag_chain(retriever)
