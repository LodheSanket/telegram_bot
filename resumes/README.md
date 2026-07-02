This folder holds the actual resume PDFs that get attached to outgoing
emails. They are not in the database, the app just looks them up by
filename based on the role.

Add these four files here:

frontend.pdf
backend.pdf
angular.pdf
fullstack.pdf

The mapping between role names and filenames lives in
services/resume_mapper.py, if you want different filenames or to add
more roles, that's the only place you need to change it.
