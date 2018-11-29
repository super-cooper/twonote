import os
import time

import git


class HistoryManager:
    """ Class for managing version history of a notebook
    """

    def __init__(self, path: str, git_dir: str = '.history', remote: str = None):
        self.git_dir = os.path.join(path, git_dir)
        self.repo: git.Repo = git.Repo.init(git_dir)
        self.remote: git.Remote = self.repo.create_remote('origin', remote) if remote is not None else None
        # TODO if remote is provided, ensure that credentials are provided as well
        self.master = self.repo.active_branch.name

    def make_checkpoint(self, message: str = None) -> bool:
        """ Creates a checkpoint in history
        :param message: The message to go with the checkpoint. If no message is provided, the default message is just a
        timestamp
        :return: The hex code of the checkpoint
        """
        commit = self.repo.index.commit(message if message is not None else time.strftime("%a, %d %b %Y %H:%M"))
        return commit.hexsha

    def switch_branch(self, branch_name: str) -> bool:
        """ Switches the branch
        :param branch_name: The name of the branch to switch to
        :return: True if the branch was switched, False otherwise
        """
        if branch_name == self.repo.active_branch:
            return False
        self.repo.git.checkout(branch_name)

    def roll_back(self, branch_id: str = None) -> bool:
        """ Effective "undo" button on a branch
        :param branch_id: The branch to roll back (default active branch)
        :return: True if the branch had commits to roll back to, False otherwise
        """
        pass

    def new_branch(self) -> str:
        """ Creates a new branch
        :return: The git hash of the new branch
        """
        pass

    def switch_to_master(self) -> None:
        """ Switches the branch to master """
        self.switch_branch(self.master)
