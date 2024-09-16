# Book Summarizer
Simple interface to summarize entire books with a slicing option to pick a range of pages.
### Using your API Key:
Create `key.json` and add your own google Gemini key. Please follow this format:

    {
        "key": "XXXXXXXXXXXXXXXXXXXXXX"
    }
The used model is Gemini Flash. 
### The first run
Pandoc will be downloaded in `/User/AppData/Local/Pandoc/` and the `.msi` installer will be created in the script directory.
Please run the installer to install Pandoc to avoid downloading everytime.

#### That's it.