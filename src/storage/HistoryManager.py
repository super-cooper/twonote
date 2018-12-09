import os
import time
from collections import defaultdict
from typing import Dict

import git


class HistoryManager:
    """ Class for managing version history of a notebook
    """

    def __init__(self, path: str, git_dir: str = '.history', remote: str = None):
        """ Constructor
        :param path: The path to the repository
        :param git_dir: The location of the git dot file TODO make use of this
        :param remote: The remote repository to back up this notebook to
        """
        self.git_dir = os.path.join(path, git_dir)
        self.repo: git.Repo = git.Repo.init(path)
        self.remote: git.Remote = self.repo.create_remote('origin', remote) if remote is not None else None
        # TODO if remote is provided, ensure that credentials are provided as well
        self.master: str = self.get_active_branch()
        self.redo_stack: Dict[str, list] = defaultdict(list)

    def make_checkpoint(self, message: str = None) -> bool:
        """ Creates a checkpoint in history
        :param message: The message to go with the checkpoint. If no message is provided, the default message is just a
        timestamp
        :return: The hex code of the checkpoint
        """
        commit = self.repo.index.commit(message if message is not None else time.strftime("%a, %d %b %Y %H:%M"))
        self.redo_stack[self.get_active_branch()] = []
        return commit.hexsha

    def switch_branch(self, branch_name: str) -> bool:
        """ Switches the branch
        :param branch_name: The name of the branch to switch to
        :return: True if the branch was switched, False otherwise
        """
        if branch_name == self.get_active_branch():
            return False
        self.repo.git.checkout(branch_name)

    def roll_back(self, branch_name: str = None) -> bool:
        """ Effective "undo" button on a branch
        :param branch_name: The branch to roll back (default active branch)
        :return: True if the branch had commits to roll back to, False otherwise
        """
        prev = self.get_active_branch()
        outcome = True
        self.switch_branch(branch_name)
        # Put the last commit onto a stack, so that redo can be used
        self.redo_stack[self.get_active_branch()].append(self.repo.git.rev_parse('HEAD'))
        try:
            self.repo.git.checkout('HEAD^1')
        except git.exc.GitCommandError:
            outcome = False
            # Nothing to redo, so remove it from the stack
            self.redo_stack[self.get_active_branch()].pop()
        finally:
            self.switch_branch(prev)
            return outcome

    def can_roll_forward(self, branch_name: str) -> bool:
        """ Tells if this history manager is capable of rolling forward through commits on a branch
        :param branch_name: The branch to check
        :return: True if this history manager can be rolled forward, False otherwise
        """
        return len(self.redo_stack[branch_name]) > 0

    def roll_forward(self, branch_name: str) -> bool:
        """ Moves the head of this branch forward one commit (effective "re-do" button)
        :param branch_name: The name of the branch to modify
        :return: True if the roll is successful, False otherwise
        """
        if not self.can_roll_forward(branch_name):
            return False
        prev = self.get_active_branch()
        self.switch_branch(branch_name)
        self.repo.git.checkout(self.redo_stack[branch_name].pop())
        self.repo.git.checkout(prev)
        return True

    def new_branch(self, branch_name: str) -> bool:
        """ Creates a new branch and switches to it
        :param branch_name: The name of the new branch
        :return: True if the branch was created, False if a branch with the given name already exists
        """
        prev = self.get_active_branch()
        self.switch_to_master()
        # Check if a branch with given name already exists
        try:
            self.repo.git.checkout(b=branch_name)
        except git.exc.GitCommandError:
            self.switch_branch(prev)
            return False
        return True

    def switch_to_master(self) -> None:
        """ Switches the branch to master """
        if not self.get_active_branch() == self.master:
            self.switch_branch(self.master)

    def get_active_branch(self) -> str:
        """ Gets the name of the current active branch
        :return: The name of the active branch
        """
        return self.repo.active_branch.name

    def get_all_edit_history(self, branch_name: str) -> str:
        """ Gets all edit history for a particular branch
        :param branch_name: The name of the branch to pull edit history from
        :return: The edit history for the branch, formatted as a git reflog
        """
        prev = self.get_active_branch()
        self.switch_branch(branch_name)
        history = self.repo.git.reflog()
        self.switch_branch(prev)
        return history
