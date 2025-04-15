# The Women in Neuroscience Repository (WiNRepo)
This GitHub public repository stands for the development of the website of WiNRepo - [https://www.winrepo.org](https://www.winrepo.org).

## Dependencies
All dependencies are listed in the [`requirements.txt`](requirements.txt) file, stored in the root directory of the repository. To install them, you can run in the main directory:

```
pip install -r requirements.txt
```

## Development
To contribute, please fork the repository. In the dev branch of your own repository, rename the file `.env.default` to `.env`.
In order to have data to run the website, run the following command to generate a mock dataset: 

```
./tools/refresh_db.sh
```

The local website uses SQLite, so there is no need to install any other dependencies.
As you develop, if you would like to revert the changes you did to your local DB, you can run the command as much as you like.
After setting up the DB, you can run the website locally using:

```
python manage.py runserver
```

and load the following page address in your browser: `http://localhost:8000/`.

### Important:
<ol>
  <li>Do not forget to hard reload the page to visualize your code changes.</li>
  <li>Please check whether your new features work in all range of different devices by enabling the <i>Responsive Design Mode</i> in your browser.</li>
</ol>

## Contributions Guidelines

To report a bug, suggest a new feature, add information or any other type of enhancement, please submit an issue. We will make all possible efforts to discuss and evaluate them with maximum brevity. When submitting a new Pull Request (PR), link it to the issues that it attempts to address through mention "Closes #XXXX".

### PR Structure
<ol>
  <li>Clear name</li>
  <li>Clearly outline goals and changes proposed</li>
  <li>Doesn’t include “unrelated” code change</li>
</ol>

### Coding Style

<ol>
  <li>Variables, functions, arguments must have clear names</li>
  <li>Follows PEP 8 -- Style Guide for Python Code: https://www.python.org/dev/peps/pep-0008</li>
  <li>Low redundancy</li>
  <li>No new dependency</li>
</ol>

## Background

This project builds upon work originally developed in the [WiNRepo repository by Gregory Fryns](https://github.com/gregoryfryns/winrepo). This legacy repository includes the initial implementation of the WiNRepo website that informed its current version. Major changes include:

<ol>
  <li>a user account functionality, enabling user registration, login, and update of user's profile in the repository.</li>
  <li>a separate 'Resources' tab alongside the existing FAQ, featuring Publications, Tips, and Academic Advice.</li>
</ol>
