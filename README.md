# The Women in Neuroscience Repository (WiNRepo)
This GitHub public repository stands for the development of the website of WiNRepo - [https://www.winrepo.org](https://www.winrepo.org).

## Dependencies
All dependencies are listed in the `requirements.txt` file, stored in the main directory of the repository. Alternatively, you can run also in the main directory:

```
pip install -r requirements.txt
```

## Development
To contribute, please fork the repository. In the dev branch of your own repository, rename the file `.env.default` to `.env`. To compile and check your changes locally, run:

```
python manage.py runserver
```

and load the following page address in your browser: `http://localhost:8000/`.

### Important:
<ol>
<li>Do not forget to hard reload the page to visualize your updates.</li>
<li>Please check whether your new features work in all range of different devices by enabling the <i>Responsive Design Mode</i> in your browser.</li>
</ol>
