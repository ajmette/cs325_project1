import ollama

with open("prompts.txt", 'r') as file:                  # open prompts file as read only
    lines = file.readlines()

for line in lines:                                      # loops for each prompt given inside prompts.txt file
    response = ollama.chat(                             # sends a prompt to ollama using phi3 model
        model = 'phi3', 
        messages = [{'role': 'user', 'content': line}], # message with two keys: 
                                                        # role is who is sending the message and 
                                                        # content is the actual message to send which is stored in 'line'
        stream = True                                   # enables real time responses instead of full response all at once
        )

    for chunk in response:                              # loops for each chunk of the response as the response comes in (since stream=True)
        with open("answers.txt", "a") as output:        # open file in append mode (writing mode that new data gets added to end of file)
            output.write(chunk['message']['content'])   # writes the phi3 response to ansers.txt file

    with open("answers.txt", 'a') as output:            # move to new line after each prompt
        output.write('\n')


file.close()                                            # close files when done
output.close()