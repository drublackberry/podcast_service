from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from flask import current_app
import logging

logger = logging.getLogger(__name__)

# Global variables for model and tokenizer
model = None
tokenizer = None

def load_model():
    """Load the embedding model and tokenizer"""
    global model, tokenizer
    if model is None or tokenizer is None:
        model_name = current_app.config['EMBEDDING_MODEL']
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            if torch.cuda.is_available():
                model = model.cuda()
            model.eval()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

def create_embedding(text):
    """Create embedding for a text segment"""
    try:
        load_model()
        
        # Tokenize and prepare input
        inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Generate embeddings
        with torch.no_grad():
            outputs = model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        # Convert to numpy and return
        if torch.cuda.is_available():
            embeddings = embeddings.cpu()
        return embeddings.numpy()[0]
    
    except Exception as e:
        logger.error(f"Error creating embedding: {str(e)}")
        return None

def compute_similarity(embedding1, embedding2):
    """Compute cosine similarity between two embeddings"""
    if embedding1 is None or embedding2 is None:
        return 0.0
    
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return np.dot(embedding1, embedding2) / (norm1 * norm2)

def find_similar_segments(query_embedding, threshold=0.7, limit=5):
    """Find segments similar to the query embedding"""
    from app.models import Segment
    
    similar_segments = []
    segments = Segment.query.all()
    
    for segment in segments:
        segment_embedding = segment.get_embedding()
        if segment_embedding is not None:
            similarity = compute_similarity(query_embedding, segment_embedding)
            if similarity >= threshold:
                similar_segments.append((segment, similarity))
    
    # Sort by similarity and return top matches
    similar_segments.sort(key=lambda x: x[1], reverse=True)
    return similar_segments[:limit]
