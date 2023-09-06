import execjs
# Define the JavaScript code as a string
js_file_path = 'dom_extractor.js'

# Read the JavaScript code from the file
with open(js_file_path, 'r') as js_file:
    js_code = js_file.read()

# Create an ExecJS context
context = execjs.compile(js_code)

# Call the JavaScript function and get the result
result = context.call("dom_extractor","hello")

# Print the result
print("Result from JavaScript:", result)