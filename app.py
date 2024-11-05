import gradio as gr
import pandas as pd
from course_search import CourseSearchSystem

# Initialize the search system
df = pd.read_csv('course_data.csv')
search_system = CourseSearchSystem()
search_system.load_and_prepare_data(df)

def search_courses(query: str, num_results: int) -> str:
    """Search function for Gradio interface"""
    if not query.strip():
        return "Please enter a search query to find relevant courses!"
    
    return search_system.search_courses(query, top_k=num_results)

# Custom CSS for better spacing while maintaining visibility
custom_css = """
.gradio-container {
    padding: 2rem !important;
}
.footer {
    margin-top: 4rem;
    text-align: center;
    font-size: 1.1em;
}
.title {
    margin-bottom: 2rem !important;
    text-align: center;
}
.search-box {
    margin: 1.5rem 0 !important;
}
.results-container {
    margin-top: 2rem !important;
    padding: 1rem !important;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 8px;
}
"""

# Create Gradio interface with improved spacing and visibility
with gr.Blocks(css=custom_css, title="Analytics Vidhya Course Search") as iface:
    gr.Markdown(
        """
        # Analytics Vidhya Free Course Search
        Find the perfect free course from Analytics Vidhya's collection using natural language search.
        Simply describe what you're looking for!
        """,
        elem_classes="title"
    )
    
    with gr.Row():
        with gr.Column():
            query_input = gr.Textbox(
                label="What would you like to learn?",
                placeholder="E.g., 'machine learning for beginners' or 'computer vision projects'",
                lines=2,
                elem_classes="search-box"
            )
            
            with gr.Row():
                num_results = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=3,
                    step=1,
                    label="Number of results to show"
                )
                search_button = gr.Button(
                    "🔍 Search Courses",
                    variant="primary",
                    scale=0.4,
                    size="lg"
                )
    
    # Results section
    output = gr.Markdown(
        label="Search Results",
        elem_classes="results-container"
    )
    
    # Footer
    gr.Markdown(
        """
        ---
        Made with Sentence Transformers and Gradio
        """,
        elem_classes="footer"
    )
    
    # Set up the click event
    search_button.click(
        fn=search_courses,
        inputs=[query_input, num_results],
        outputs=output
    )

if __name__ == "__main__":
    iface.launch(
        share=False,
        debug=False,
        show_api=False,
        show_error=False
    )