# Agentic Essay Assistant

### About
This project is an attempt to create a user-friendly web-deployeable agentic solution which has tools targeted at editing, researching, and evaluating essays. 

It uses HTML, JS, and CSS for a web frontend, which then connects to a Python backend using Flask. This user interface makes it more user-friendly than most existing agentic solutions.

### TODO List
- [x] Update site fetcher and citer to use headless browser to bypass bot detection
- [ ] Add editing tools for the agent
- [x] Offload site reading to other agent to decrease context in main ReACT loop
- [ ] Allow agent to leave notes for the user

### PreRequisites
This project depends on the OpenAI API, and the Google Custom Search API. Note that you will be required to provide API keys for these services, as well as a Google Custom Search Engine identifier. On the first runthrough of the program, it will notify you that you do not have these keys, and it will create a blank template for you to input them into. 

Once this happens, open ./.secret/keys.wallet in a text editor, and paste the relevant API keys into the spaces provided. Once this happens, the project should be ready to deploy.

### Running
To run a local instance of this project, first call load.bat from a CMD instance in the top-level project directory. This will add all of the relevant batch scripts to the current working directory.

Next, call setup.bat, which will create a virtual environment (./env) in the top-level directory,activate it, and download several necessary libraries into that virtual environemnt.

You should already be in the virtual environment at this point, but for future runs, it is sufficient just to call enter.bat. This will place you in the virtual environment you installed earlier, without the extra overhead of setting up a new environemnt.

At this point, you should be ready to start the server. Call run.bat, which will execute the main.py file and start the server. Your terminal should now show the local web adress where the front-end is live. Paste this adress into your browser, and you will see the website.

### Use
Once you load an existing essay, either by uploading a pdf or copying some plaintext, you will have access to all of the controls in the righthand control panel. 

This tool uses the USAFA DF GenAI levels, which allows a teacher to specify the ways in which AI can be used for an assignment. Because this project is targeted at Cadets, it allows an AI level to be specified at the beginning. This level will determine what sorts of tools the AI agent will have access to. Because the AI Agent never gets to converse with you, and because the tools are the only way that it can interact with you or your writing, these tool-access limitations prevent it from providing unauthorized help.

Once you specified the AI Level, the essay text, the available tools, and the additional instructions (what you actually want it to do), you are ready to hit run. This will begin the Agentic ReACT cycle on your serverside environment. This may take a while, but progress can be tracked on the serverside terminal.

Once done, the results will be uploaded to the frontend for viewing. These results will include a modified version of the essay (if the Agent was given editing tools), a transcript of the ReACT process (which can be accessed in the "Transcript" tab), and optionally several additional files which the program outputted (i.e. documentation statements, works cited, etc.).
