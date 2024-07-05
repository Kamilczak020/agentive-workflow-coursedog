from pipelines.master import run_master_pipeline
from import_from_db import import_all_from_db
import gradio as gr

# import_all_from_db()

current_text = '### Information Column\n'

def get_value():
    return current_text

def update_info(new_text: str):
    global current_text
    current_text += f'\n\n{new_text}'

def clear_all():
    global current_text
    current_text = ''

def chat_function(message, history):
    response = run_master_pipeline(message, update_info)
    history.append((message, response))
    return response, history

def add_info_block(info, current_info):
    if current_info:
        return current_info + "\n\n" + info
    return info

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot()
            msg = gr.Textbox()
            clear = gr.Button("Clear")

        with gr.Column():
           info = gr.Markdown(value=get_value, every=1, elem_id="info_column")

    msg.submit(chat_function, inputs=[msg, chatbot], outputs=[msg, chatbot])
    clear.click(clear_all, None, chatbot, queue=False)

demo.launch()
