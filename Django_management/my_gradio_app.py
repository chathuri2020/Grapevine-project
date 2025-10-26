import gradio as gr

# Your existing Gradio function(s). 
# Note the addition of the 'request: gr.Request' parameter, which allows 
# the Gradio function to access cookies, headers, etc., passed from the browser.
def secure_ml_function(input_data, request: gr.Request):
    # Optional: You can check for headers/cookies here, though FastAPI handles the *security*.
    # user_info = request.headers.get("X-User-Info", "Anonymous") 
    
    return f"Result for data: {input_data}. Access Confirmed for an authenticated session."

# Your existing Gradio Blocks/Interface structure
with gr.Blocks() as demo:
    gr.Markdown("## Authenticated App Component")
    text_input = gr.Textbox(label="Enter Data:")
    output = gr.Textbox(label="Result")
    
    # Pass gr.Request as an input to your function
    text_input.submit(secure_ml_function, inputs=[text_input, gr.Request], outputs=output)

# CRITICAL: This line extracts the underlying Starlette/FastAPI app object.
gradio_app_asgi = demo.app