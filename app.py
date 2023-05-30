import os
import pandas as pd
import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        message = request.form["message"]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=generate_prompt(message),
            temperature=0.3,
        )
        return redirect(url_for("index", result=response['choices'][0]['message']['content'].replace('\n\n', '<br>')))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(message):

    df = pd.read_csv('overdue_findings.csv')
    # Function to join columns with a comma
    def join_columns(row):
        return ", ".join(row.astype(str))

    # Combine columns A, B, and C into a new column 'Combined'
    df['Combined'] = df.agg(join_columns, axis=1)

    columns_string = ", ".join(df.columns)
    df_string = ''
    for i in range(len(df)):
        df_string = df_string + str(i + 1) + '. ' + df['Combined'][i] + '\n'

    msg_1 = "You're the Risk control findings explainer."
    msg_2 = f"You will get the data read from file with the following columns: {columns_string}. " \
            f"the data wil be separated by commas"
    msg_3 = f"{message}, the response should be html readable. The data is here: {df_string}."

    messages_roles = ["system", "assistant", "user"]
    messages_list = [msg_1, msg_2, msg_3]
    combined_messages = []
    for i in range(len(messages_list)):
        combined_messages.append({"role": messages_roles[i], "content": messages_list[i]})

    return combined_messages
