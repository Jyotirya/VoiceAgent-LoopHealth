import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os

class HospitalRAG:
    def __init__(self, csv_path='hospitals.csv'):
        self.df = pd.DataFrame()
        self.index = None
        self.model = None
        self.embeddings = None
        
        try:
            print("🔄 RAG STEP 0: Loading CSV Data...")
            self.df = pd.read_csv(csv_path, encoding='utf-8')
            
            # Clean columns
            self.df.columns = [c.lower().strip() for c in self.df.columns]
            
            # Create "Chunks" for the Vector Search
            # We combine important fields into one rich text block per hospital
            self.df['rag_text'] = self.df.apply(
                lambda x: f"Hospital: {x.get('hospital name', 'Unknown')}. "
                          f"City: {x.get('city', 'Unknown')}. "
                          f"Address: {x.get('address', 'Unknown')}. "
                          f"State: {x.get('state', 'Unknown')}.", 
                axis=1
            )
            
            print(f"✅ Data Loaded: {len(self.df)} rows.")

            # --- RAG INITIALIZATION ---
            print("⏳ RAG STEP 1: Loading Embedding Model (all-MiniLM-L6-v2)...")
            # This runs locally and is free. It turns text into numbers.
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            print("⚗️ RAG STEP 2: Creating Embeddings for Database...")
            # Convert all hospital descriptions to vectors
            self.embeddings = self.model.encode(self.df['rag_text'].tolist(), show_progress_bar=True)
            
            print("🗂️ RAG STEP 3: Building FAISS Vector Index...")
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(self.embeddings).astype('float32'))
            
            print("🚀 RAG System Ready!")

        except Exception as e:
            print(f"❌ Error initializing RAG: {e}")

    def search(self, query, k=3):
        if self.index is None:
            return "Error: RAG Database not initialized."

        print(f"🔎 RAG Search Query: '{query}'")

        # --- 1. QUERY EMBEDDING ---
        # Convert user question into a vector
        query_vector = self.model.encode([query])

        # --- 2. VECTOR SEARCH ---
        # Search FAISS for the K nearest neighbors
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)

        # --- 3. RETRIEVE TOP K RESULTS ---
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.df):
                row = self.df.iloc[idx]
                results.append(row['rag_text'])

        # --- 4. BUILD CONTEXT (Internal) ---
        # Format the results as a single string for the LLM
        context_text = "\n\n".join([f"Result {i+1}: {text}" for i, text in enumerate(results)])
        
        return context_text

# Singleton instance
rag_system = HospitalRAG()