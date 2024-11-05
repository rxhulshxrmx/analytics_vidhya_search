import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import re
import torch
from transformers import AutoModel, AutoTokenizer

class CourseSearchSystem:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model_name = 'sentence-transformers/all-MiniLM-L6-v2'
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
        self.model.eval()
            
    def mean_pooling(self, model_output, attention_mask):
        """Mean pooling to get sentence embeddings"""
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for a list of texts"""
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=512)
        encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}

        with torch.no_grad():
            model_output = self.model(**encoded_input)

        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
        
        return sentence_embeddings.cpu().numpy()

    def preprocess_text(self, text: str) -> str:
        """Clean and standardize text data"""
        if pd.isna(text):
            return ""
        text = str(text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        return text.lower()
    
    def prepare_course_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare and clean course data"""
        free_courses = df[df['Course Name'].str.contains('Free', case=False, na=False)]
        
        free_courses = free_courses.fillna({
            'Course Time': 0,
            'Ratings': 4.6,
            'Difficulty': 'Beginner',
            'Key Takeaways': 'Course details not available.'
        })
        
        free_courses['search_text'] = free_courses.apply(
            lambda x: f"{x['Course Name']} {x['Key Takeaways']} {x['Difficulty']}", 
            axis=1
        )
        
        free_courses['search_text'] = free_courses['search_text'].apply(self.preprocess_text)
        
        return free_courses
    
    def load_and_prepare_data(self, df: pd.DataFrame):
        """Load and prepare the course data and generate embeddings"""
        self.courses_df = self.prepare_course_data(df)
        self.course_embeddings = self.get_embeddings(self.courses_df['search_text'].tolist())

    def generate_response(self, query: str, results: List[Dict]) -> str:
        """Generate a professional response with course recommendations"""
        response_parts = []
        
        # Introduction based on number of results
        if len(results) == 1:
            response_parts.append(f"I found an excellent free course matching your search for '{query}':")
        else:
            response_parts.append(f"I found {len(results)} relevant free courses matching your search for '{query}':")
        
        # Course details
        for i, result in enumerate(results, 1):
            course_name = result['course_name']
            course_section = f"\n**{i}. {course_name}**\n"
            
            # Clean rating display
            rating = result['ratings']
            rating_display = f"{rating}/5.0"
            course_section += f"**Rating:** {rating_display}\n"
            
            # Add difficulty
            course_section += f"**Level:** {result['difficulty']}\n"
            
            # Add duration if available
            if result['course_time']:
                course_section += f"**Duration:** {result['course_time']} hours\n"
            
            # Format key takeaways with bullet points
            if result['key_takeaways'] and result['key_takeaways'] != 'Course details not available.':
                course_section += "\n**What you'll learn:**\n"
                takeaways = result['key_takeaways'].split('.,')
                formatted_takeaways = []
                for takeaway in takeaways:
                    cleaned = takeaway.strip('. ,')
                    if cleaned:
                        if len(cleaned) > 100:
                            cleaned = cleaned[:97] + "..."
                        formatted_takeaways.append(f"• {cleaned}")
                course_section += "\n".join(formatted_takeaways[:3])
                
                if len(takeaways) > 3:
                    course_section += "\n• And more..."
            
            # Add relevance score as a percentage
            similarity_percentage = int(result['similarity_score'] * 100)
            course_section += f"\n**Match Score:** {similarity_percentage}%"
            
            # Add course link
            course_section += f"\n\n[Start Course]({result['url']})\n"
            
            response_parts.append(course_section)
        
        # Add helpful conclusion
        response_parts.append("\n---\n")
        response_parts.append("**Notes:**")
        response_parts.append("• Courses are sorted by relevance to your search")
        response_parts.append("• All courses are free and include hands-on projects")
        response_parts.append("• Certificates are provided upon completion")
        
        return "\n".join(response_parts)
    
    def search_courses(self, query: str, top_k: int = 5) -> str:
        """Search for courses and return formatted response"""
        query = self.preprocess_text(query)
        query_embedding = self.get_embeddings([query])[0]
        similarities = np.dot(self.course_embeddings, query_embedding)
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            course = self.courses_df.iloc[idx]
            results.append({
                'course_name': course['Course Name'],
                'key_takeaways': course['Key Takeaways'],  # Fixed: Changed from Key_Takeaways to Key Takeaways
                'course_time': course['Course Time'],
                'ratings': course['Ratings'],
                'difficulty': course['Difficulty'],
                'similarity_score': similarities[idx],
                'url': course['Website']
            })
        
        return self.generate_response(query, results)