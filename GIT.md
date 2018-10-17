# How to use git for this project

For this project, we're going to have a really simple git workflow so we don't
have to worry about anything. It's may not be best practice, but it's easy
and there's only 5 of us. First start by cloning the project to your local machine
with `git clone https://github.com/super-cooper/twonote.git`.

1. When contributing a new feature, create a new branch off of master
```
git checkout -b <branch-name>
```

2. Write whatever code you want to write. If you create a new file or directory, be sure to
add it to the tracking list (I don't recommend using `git add -A`)
```
git add <path-to-file>
```
If there is a file or directory that you very specifically *do not* want to be tracked, make
sure to add it to the `.gitignore` file

3. When you want to save your changes, first make sure your code obeys the style
guide by running `./lint.sh`

4. To commit your changes to the repository, use
```
git commit <file(s)> -m "<message>"
```
Every commit needs to have a message. If you want to commit every change that you
have made since your last commit, you can use the shorthand `git commit -a -m "<message>"`,
or even shorter `git commit -am "<message>"`

5. When you want to upload your branch to the GitHub repository, do it with
```
git push origin <your-branch-name>
```

6. To fetch changes that other people have made to the GitHub repository, use
```
git fetch
```
I recommend doing this before every programming session

7. To switch to another branch, use
```
git checkout <branch-name>
```
If you want to go back to the last branch you were on, use the shorthand
```
git checkout -
```
The main branch of the project will be called `master`. Please don't write any
large changes to master before conferring with the group. Editing master is how
nasty merge conflicts tend to happen.

8. To see all the branches in the repository, use
```
git branch -a
```
