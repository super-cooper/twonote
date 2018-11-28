import os

import git


class HistoryManager:
    """ Class for managing version history of a notebook
    """

    def __init__(self, path: str, git_dir: str = '.git', remote: str = None):
        self.git_dir = os.path.join(path, git_dir)
        self.repo = git.Repo.init(path)
        self.remote = remote
        # TODO if remote is provided, ensure that credentials are provided as well
        # TODO save master hash as class variable
        self.master = None

    def make_checkpoint(self, message: str = None) -> bool:
        """ Creates a checkpoint in history
        :param message: The message to go with the checkpoint. If no message is provided, the default message is just a
        timestamp
        :return: True if the checkpoint is successfully created, False otherwise
        """
        pass

    def switch_branch(self, branch_id: str) -> bool:
        """ Switches the branch
        :param branch_id: The git hash of the branch to switch to
        :return: True if the branch was switched, False otherwise
        """
        pass

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
